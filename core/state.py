import json, os, threading
from config import OWNER_ID, ADMIN_ID, DATA_DIR

class State:
    def __init__(self):
        self._lock = threading.RLock()
        self._state = {}
        self._pay_state = {}
        self.active_users = set()
        self.bot_locked = False
        self.force_sub_enabled = False
        self._admins_path = os.path.join(DATA_DIR, "admins.json")
        self.admin_ids = {int(OWNER_ID), int(ADMIN_ID)}
        self._load_admins()
    def _load_admins(self):
        try:
            with open(self._admins_path, "r", encoding="utf-8") as f:
                self.admin_ids.update(int(x) for x in json.load(f))
        except Exception: pass
        self.admin_ids.add(int(OWNER_ID))
    def _save_admins(self):
        os.makedirs(os.path.dirname(self._admins_path), exist_ok=True)
        tmp = self._admins_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f: json.dump(sorted(self.admin_ids), f)
        os.replace(tmp, self._admins_path)
    def is_admin(self, uid): return int(uid) in self.admin_ids or int(uid) == int(OWNER_ID)
    def add_admin(self, uid):
        with self._lock: self.admin_ids.add(int(uid)); self._save_admins()
    def remove_admin(self, uid):
        with self._lock:
            uid=int(uid)
            if uid == int(OWNER_ID): return False
            self.admin_ids.discard(uid); self._save_admins(); return True
    def set_state(self, uid, value):
        with self._lock: self._state[int(uid)] = value
    def get_state(self, uid):
        with self._lock: return self._state.get(int(uid))
    def clear_state(self, uid):
        with self._lock: self._state.pop(int(uid), None)
    def set_pay_state(self, uid, value):
        with self._lock: self._pay_state[int(uid)] = value
    def get_pay_state(self, uid):
        with self._lock: return self._pay_state.get(int(uid))
    def clear_pay_state(self, uid):
        with self._lock: self._pay_state.pop(int(uid), None)

state = State()
bot_scripts = {}
