import os,sys,time,subprocess,threading,shutil,zipfile,logging,datetime,venv,hashlib
from config import (UPLOAD_DIR, BACKUP_DIR, LOGS_DIR, DATA_DIR, PLAN_LIMITS, BRAND_TAG,
                    OWNER_ID, DAILY_REPORT_HOUR, DAILY_REPORT_MINUTE,
                    FREE_BOT_MAX_HOURS, MAIN_BOT_AUTO_RESTART_HOURS)
from core.state import bot_scripts
from utils.helpers import user_folder, is_running, kill_tree, cleanup_script
logger=logging.getLogger("TYNEX.RUNNER")
_bot=None; _db=None; _forward_error=None; _safe_send=None
_start_locks = {}
_start_locks_guard = threading.Lock()
class Detector:
    @staticmethod
    def report(folder):
        if not os.path.isdir(folder): return None,"py",0
        candidates=("main.py","bot.py","app.py","index.js","server.js")
        for name in candidates:
            p=os.path.join(folder,name)
            if os.path.isfile(p):
                return name,("node" if name.endswith(".js") else "py"),0.95
        for current, dirs, files in os.walk(folder):
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", ".venv", "venv")]
            for name in files:
                if name.endswith(".py"): return os.path.relpath(os.path.join(current,name),folder),"py",0.65
                if name.endswith(".js"): return os.path.relpath(os.path.join(current,name),folder),"node",0.65
        return None,"py",0.0
det=Detector()
def init_runner(bot,db,forward_error,safe_send):
    global _bot,_db,_forward_error,_safe_send
    _bot=bot;_db=db;_forward_error=forward_error;_safe_send=safe_send

def _project_lock(key):
    with _start_locks_guard:
        return _start_locks.setdefault(str(key), threading.Lock())

def _log_line(log, message):
    try:
        log.write(str(message) + "\n")
        log.flush()
    except Exception:
        pass

def prepare_project_dependencies(path, file_type, log):
    """Install project dependencies once per requirements/package manifest fingerprint."""
    if file_type == "node":
        package = os.path.join(path, "package.json")
        if os.path.isfile(package):
            npm = shutil.which("npm")
            if not npm:
                raise RuntimeError("Node.js project needs npm, but npm is not installed on the hosting server.")
            manifest_hash = hashlib.sha256(open(package, "rb").read()).hexdigest()
            marker = os.path.join(path, ".tynex_npm_install_hash")
            if not os.path.isfile(marker) or open(marker, encoding="utf-8").read().strip() != manifest_hash:
                _log_line(log, "[TYNEX] Installing Node.js dependencies (npm install)...")
                result = subprocess.run([npm, "install", "--no-audit", "--no-fund"], cwd=path,
                                         stdout=log, stderr=subprocess.STDOUT, timeout=300, check=False)
                if result.returncode:
                    raise RuntimeError(f"npm install failed with exit code {result.returncode}; see project logs.")
                with open(marker, "w", encoding="utf-8") as fh: fh.write(manifest_hash)
        return [shutil.which("node") or "node"]

    venv_dir = os.path.join(path, ".venv")
    py_bin = os.path.join(venv_dir, "Scripts", "python.exe") if os.name == "nt" else os.path.join(venv_dir, "bin", "python")
    if not os.path.isfile(py_bin):
        _log_line(log, "[TYNEX] Creating isolated Python virtual environment...")
        venv.EnvBuilder(with_pip=True, clear=False).create(venv_dir)
    req = os.path.join(path, "requirements.txt")
    if os.path.isfile(req):
        manifest_hash = hashlib.sha256(open(req, "rb").read()).hexdigest()
        marker = os.path.join(path, ".tynex_requirements_hash")
        installed_hash = open(marker, encoding="utf-8").read().strip() if os.path.isfile(marker) else ""
        if installed_hash != manifest_hash:
            _log_line(log, "[TYNEX] Installing requirements.txt into project .venv...")
            result = subprocess.run([py_bin, "-m", "pip", "install", "--disable-pip-version-check", "-r", req],
                                    cwd=path, stdout=log, stderr=subprocess.STDOUT, timeout=600, check=False)
            if result.returncode:
                raise RuntimeError(f"pip install failed with exit code {result.returncode}; see project logs.")
            with open(marker, "w", encoding="utf-8") as fh: fh.write(manifest_hash)
    return [py_bin]

def _prepare_runtime(path, file_type, log):
    """Reuse the project-local environment; unchanged manifests are not reinstalled."""
    return prepare_project_dependencies(path, file_type, log)

def run_bot_script(bot_id,user_id):
    b=_db.get_bot(str(bot_id))
    if not b:return
    key=f"{int(b['user_id'])}_{b['bot_name']}"
    lock = _project_lock(key)
    if not lock.acquire(blocking=False):
        return
    try:
        current = bot_scripts.get(key)
        if current:
            proc = current.get("process")
            if proc and proc.poll() is None:
                return
            cleanup_script(key)

        path=b.get("file_path") or user_folder(user_id)
        path=os.path.realpath(path)
        if not os.path.isdir(path):
            _db.update_bot(bot_id,status="error")
            if _safe_send:_safe_send(user_id,"❌ Project folder was not found on the server.")
            return
        entry=b.get("entry_file") or "main.py"
        target=os.path.realpath(os.path.join(path,entry))
        if os.path.commonpath([path,target]) != path or not os.path.isfile(target):
            _db.update_bot(bot_id,status="error")
            if _safe_send:_safe_send(user_id,"❌ Project entry file was not found.")
            return

        os.makedirs(LOGS_DIR,exist_ok=True)
        log_path=os.path.join(LOGS_DIR,f"bot_{bot_id}.log")
        log=open(log_path,"a",encoding="utf-8",errors="replace",buffering=1)
        _db.update_bot(bot_id,status="starting",last_started=datetime.datetime.now().isoformat())
        _log_line(log, "\n" + "="*60)
        _log_line(log, f"[TYNEX] Starting project #{bot_id}: {b.get('bot_name',entry)}")
        try:
            prefix = _prepare_runtime(path, b.get("file_type","py"), log)
            cmd = prefix + [target] if b.get("file_type","py") == "node" else prefix + ["-u", target]
            _log_line(log, "[TYNEX] Launch command prepared; starting project.")
            env=os.environ.copy()
            if b.get("file_type","py") == "py":
                env["VIRTUAL_ENV"] = os.path.join(path, ".venv")
                env["PATH"] = os.path.join(env["VIRTUAL_ENV"], "bin") + os.pathsep + env.get("PATH","")
            proc=subprocess.Popen(cmd,cwd=path,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,
                                  env=env,start_new_session=True)
            bot_scripts[key]={"process":proc,"bot_id":str(bot_id),"user_id":int(b['user_id']),
                              "file_name":b.get("bot_name",entry),"start_time":time.time(),"log_handle":log}
            time.sleep(1)
            if proc.poll() is not None:
                _db.update_bot(bot_id,status="crashed",last_crash=datetime.datetime.now().isoformat())
                _log_line(log, f"[TYNEX] Process exited immediately with code {proc.returncode}.")
                cleanup_script(key)
                if _safe_send:_safe_send(user_id,f"❌ Project stopped during startup. Open Logs for the exact error. (#{bot_id})")
            else:
                _db.update_bot(bot_id,status="running")
                if _safe_send:_safe_send(user_id,f"✅ Project started. Logs: My Bots → View Logs (#{bot_id})")
        except Exception as exc:
            _log_line(log, f"[TYNEX] START ERROR: {type(exc).__name__}: {exc}")
            _db.update_bot(bot_id,status="error",last_crash=datetime.datetime.now().isoformat())
            if _forward_error:_forward_error("run_bot_script",exc,user_id)
            if _safe_send:_safe_send(user_id,f"❌ Could not start project #{bot_id}. Check View Logs.")
            try: log.close()
            except Exception: pass
    finally:
        lock.release()

def thread_monitor():
    while True:
        try:
            for key,info in list(bot_scripts.items()):
                p=info.get("process")
                if p and p.poll() is not None:
                    bid=info.get("bot_id")
                    if bid:
                        _db.update_bot(bid,status="stopped",last_stopped=datetime.datetime.now().isoformat())
                    cleanup_script(key)
        except Exception:logger.exception("monitor error")
        time.sleep(10)
def thread_backup():
    while True:
        try:
            os.makedirs(BACKUP_DIR,exist_ok=True)
            stamp=datetime.datetime.now().strftime("%Y%m%d_%H%M")
            db_path=os.path.join(DATA_DIR,"naruto.db")
            if os.path.isfile(db_path):
                shutil.copy2(db_path,os.path.join(BACKUP_DIR,f"database_{stamp}.db"))
            old=sorted([os.path.join(BACKUP_DIR,x) for x in os.listdir(BACKUP_DIR)],key=os.path.getmtime)
            for p in old[:-5]:
                try:os.remove(p)
                except Exception:pass
        except Exception:logger.exception("backup error")
        time.sleep(3600)
def thread_expiry():
    while True:
        try:
            for u in _db.get_all_users():
                if u.get("plan") not in (None,"free") and not u.get("is_lifetime") and not _db.is_active(u["user_id"]):
                    _db.rem_sub(u["user_id"])
        except Exception:logger.exception("expiry error")
        time.sleep(300)
def thread_storage_monitor():
    while True:
        try:
            from database import storage_monitor
            storage_monitor.check(_safe_send, list(__import__("core.state",fromlist=["state"]).state.admin_ids))
        except Exception:logger.exception("storage monitor error")
        time.sleep(1800)
def thread_daily_report():
    last_report_date = None
    while True:
        try:
            now = datetime.datetime.now()
            if (now.hour, now.minute) >= (DAILY_REPORT_HOUR, DAILY_REPORT_MINUTE) and last_report_date != now.date():
                stats = _db.stats()
                running = sum(1 for key in list(bot_scripts) if is_running(key))
                report = (f"📊 <b>{BRAND_TAG} — DAILY REPORT</b>\\n\\n"
                          f"👥 Users: {stats.get('users', 0)}\\n"
                          f"🤖 Bots: {stats.get('bots', 0)} | Running: {running}\\n"
                          f"💎 Active subscriptions: {stats.get('active_subs', 0)}\\n"
                          f"💳 Pending payments: {stats.get('pending', 0)}\\n"
                          f"💰 Revenue: {stats.get('revenue', 0)} BDT")
                if _safe_send:
                    for aid in list(__import__("core.state", fromlist=["state"]).state.admin_ids):
                        _safe_send(aid, report)
                last_report_date = now.date()
        except Exception:
            logger.exception("daily report error")
        time.sleep(30)

def thread_free_bot_limit():
    while True:
        try:
            if FREE_BOT_MAX_HOURS > 0:
                cutoff = time.time() - FREE_BOT_MAX_HOURS * 3600
                for key, info in list(bot_scripts.items()):
                    started = info.get("start_time") or time.time()
                    if started <= cutoff:
                        kill_tree(info)
                        bid = info.get("bot_id")
                        if bid: _db.update_bot(bid, status="stopped", last_stopped=datetime.datetime.now().isoformat())
                        cleanup_script(key)
                        if _safe_send: _safe_send(info.get("user_id"), "⏱️ 𝐅𝐫𝐞𝐞 𝐩𝐥𝐚𝐧 𝐫𝐮𝐧 𝐭𝐢𝐦𝐞 𝐥𝐢𝐦𝐢𝐭 𝐫𝐞𝐚𝐜𝐡𝐞𝐝.")
        except Exception:
            logger.exception("free bot limit error")
        time.sleep(60)

def thread_main_bot_restart():
    interval = max(1, MAIN_BOT_AUTO_RESTART_HOURS) * 3600
    deadline = time.time() + interval
    while True:
        if time.time() >= deadline:
            logger.warning("Scheduled main process restart requested")
            os.execv(sys.executable, [sys.executable] + sys.argv)
        time.sleep(30)
