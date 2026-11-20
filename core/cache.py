import time, threading
class _Cache:
    def __init__(self):
        self._data={}
        self._lock=threading.RLock()
    def get(self,key):
        with self._lock:
            item=self._data.get(key)
            if not item:return None
            value,expires=item
            if expires and expires<time.time():
                self._data.pop(key,None);return None
            return value
    def set(self,key,value,ex=None):
        with self._lock:self._data[key]=(value,time.time()+ex if ex else None)
    def delete(self,key):
        with self._lock:self._data.pop(key,None)
    def clear(self):
        with self._lock:self._data.clear()
cache=_Cache()
def user_cache_del(uid):cache.delete(f"user:{uid}")
def plan_cache_del(uid):cache.delete(f"plan:{uid}")
def stats_cache_invalidate():cache.delete("admin:stats")
def channels_cache_invalidate():cache.delete("channels:active")
