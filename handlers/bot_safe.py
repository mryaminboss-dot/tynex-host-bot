import re, logging
logger=logging.getLogger("TYNEX")
_UP="ABCDEFGHIJKLMNOPQRSTUVWXYZ"; _LO="abcdefghijklmnopqrstuvwxyz"
_BUP="𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙"
_BLO="𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳"
_TRANS=str.maketrans(_UP+_LO,_BUP+_BLO)
def stylish(text):
    if not isinstance(text,str): return text
    protected=[]
    def hold(m):
        protected.append(m.group(0)); return f"\uE000{len(protected)-1}\uE001"
    # Keep markup, URLs, code and @usernames unchanged.
    text=re.sub(r"<code>.*?</code>|<pre>.*?</pre>|<[^>]+>|&(?:amp|lt|gt|quot|#\d+);|https?://[^\s<>]+|@[A-Za-z0-9_]{3,}",hold,text,flags=re.I|re.S)
    text=text.translate(_TRANS)
    for i,item in enumerate(protected): text=text.replace(f"\uE000{i}\uE001",item)
    return text
def init_safe(bot,owner_id):
    global _bot,_owner
    _bot=bot; _owner=int(owner_id)
def safe_send(chat_id,text,**kwargs):
    try: return _bot.send_message(chat_id,stylish(str(text)),**kwargs)
    except Exception as exc: logger.warning("send failed: %s",exc); return None
def safe_edit(text,chat_id,message_id,**kwargs):
    try: return _bot.edit_message_text(stylish(str(text)),chat_id,message_id,**kwargs)
    except Exception as exc:
        if "message is not modified" not in str(exc).lower(): logger.warning("edit failed: %s",exc)
        return None
def safe_delete(chat_id,message_id):
    try: return _bot.delete_message(chat_id,message_id)
    except Exception: return None
def safe_answer(callback_id,text=None,show_alert=False):
    try: return _bot.answer_callback_query(callback_id,text=stylish(text) if text else None,show_alert=show_alert)
    except Exception: return None
def safe_reply(message,text,**kwargs):
    return safe_send(message.chat.id,text,reply_to_message_id=message.message_id,**kwargs)
def forward_error(where,exc,uid=None): logger.error("%s | uid=%s | %s",where,uid,exc,exc_info=True)
def forward_crash(where,exc,uid=None): logger.exception("%s crashed | uid=%s: %s",where,uid,exc)
