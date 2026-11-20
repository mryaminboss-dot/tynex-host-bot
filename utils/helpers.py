import os,time,secrets,datetime
from config import UPLOAD_DIR
try: import psutil
except Exception: psutil=None
_START=time.time(); _RATE={}
def get_uptime(): return str(datetime.timedelta(seconds=int(time.time()-_START)))
def fmt_size(size):
    n=float(size or 0)
    for unit in ("B","KB","MB","GB"):
        if n<1024 or unit=="GB": return f"{n:.1f} {unit}"
        n/=1024
def gen_ref_code(uid): return f"TX{int(uid):x}{secrets.token_hex(2).upper()}"
def time_left(value):
    if not value: return "Expired / Not set"
    try:
        if isinstance(value,str): value=datetime.datetime.fromisoformat(value)
        delta=value-datetime.datetime.now()
        return "Expired" if delta.total_seconds()<=0 else str(delta).split(".")[0]
    except Exception: return str(value)
def user_folder(uid):
    p=os.path.join(UPLOAD_DIR,str(int(uid))); os.makedirs(p,exist_ok=True); return p
def is_running(key):
    try:
        from core.state import bot_scripts
        x=bot_scripts.get(str(key)); p=x.get("process") if x else None
        return bool(p and p.poll() is None)
    except Exception: return False
def bot_running(uid,name): return is_running(f"{int(uid)}_{name}")
def cleanup_script(key):
    from core.state import bot_scripts
    x=bot_scripts.pop(str(key),None)
    if x:
        try:
            if x.get("log_handle"): x["log_handle"].close()
        except Exception: pass
def kill_tree(info):
    if not info:return
    p=info.get("process") if isinstance(info,dict) else info
    if not p:return
    try:
        if psutil:
            proc=psutil.Process(p.pid)
            for child in proc.children(recursive=True):
                try: child.terminate()
                except Exception: pass
            try: proc.terminate(); proc.wait(timeout=3)
            except Exception:
                try: proc.kill()
                except Exception: pass
        else:
            p.terminate()
            try:p.wait(timeout=3)
            except Exception:p.kill()
    except Exception: pass
def bot_res(key):
    try:
        from core.state import bot_scripts
        x=bot_scripts.get(str(key)); p=x.get("process") if x else None
        if not p or p.poll() is not None or not psutil:return 0,0
        q=psutil.Process(p.pid)
        return round(q.memory_info().rss/1048576,1),round(q.cpu_percent(interval=.1),1)
    except Exception:return 0,0
def sys_stats():
    if psutil:
        try:return {"cpu":round(psutil.cpu_percent(.1),1),"mem":round(psutil.virtual_memory().percent,1),"disk":round(psutil.disk_usage("/").percent,1),"up":get_uptime()}
        except Exception:pass
    return {"cpu":0,"mem":0,"disk":0,"up":get_uptime()}
def rate_check(uid,limit=8,window=5):
    now=time.time(); b=_RATE.setdefault(int(uid),[])
    b[:]=[x for x in b if now-x<window]
    if len(b)>=limit:return False
    b.append(now);return True
