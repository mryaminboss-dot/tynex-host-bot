from telebot import types
_db=None
def init_keyboards(db):
    global _db
    _db=db
def _btn(label,data):return types.InlineKeyboardButton(label,callback_data=data)
def main_menu_kb(uid):
    from core.state import state
    m=types.InlineKeyboardMarkup(row_width=2)
    m.row(_btn("🚀 𝐃𝐞𝐩𝐥𝐨𝐲 𝐁𝐨𝐭", "menu_deploy"), _btn("📂 𝐌𝐲 𝐏𝐫𝐨𝐣𝐞𝐜𝐭𝐬", "menu_mybots"))
    m.row(_btn("💎 𝐏𝐥𝐚𝐧𝐬 & 𝐏𝐫𝐢𝐜𝐢𝐧𝐠", "menu_sub"), _btn("🎟 𝐑𝐞𝐝𝐞𝐞𝐦 𝐂𝐨𝐝𝐞", "menu_redeem"))
    m.row(_btn("👛 𝐌𝐲 𝐖𝐚𝐥𝐥𝐞𝐭", "menu_wallet"), _btn("🎁 𝐑𝐞𝐟𝐞𝐫 & 𝐄𝐚𝐫𝐧", "menu_ref"))
    m.row(_btn("🔔 𝐍𝐨𝐭𝐢𝐟𝐢𝐜𝐚𝐭𝐢𝐨𝐧𝐬", "menu_notif"), _btn("🚄 𝐒𝐩𝐞𝐞𝐝 𝐓𝐞𝐬𝐭", "menu_speed"))
    m.row(_btn("📊 𝐒𝐭𝐚𝐭𝐢𝐬𝐭𝐢𝐜𝐬", "menu_stats"), _btn("🆘 𝐇𝐞𝐥𝐩 & 𝐒𝐮𝐩𝐩𝐨𝐫𝐭", "menu_help"))
    if state.is_admin(uid):m.row(_btn("👑 𝐀𝐝𝐦𝐢𝐧 𝐏𝐚𝐧𝐞𝐥", "menu_admin"))
    return m

def help_menu_kb():
    m=types.InlineKeyboardMarkup(row_width=1)
    m.add(_btn("🚀 𝐃𝐞𝐩𝐥𝐨𝐲 𝐆𝐮𝐢𝐝𝐞", "help_deploy"),types.InlineKeyboardButton("💬 𝐂𝐨𝐧𝐭𝐚𝐜𝐭 𝐒𝐮𝐩𝐩𝐨𝐫𝐭", url="https://t.me/MrTripleR_YT"),_btn("🏠 𝐌𝐚𝐢𝐧 𝐌𝐞𝐧𝐮", "go_home"))
    return m

def back_btn(data="go_home",label="⬅️ 𝐁𝐚𝐜𝐤"):
    m=types.InlineKeyboardMarkup();m.add(_btn(label,data));return m
def back_help_btn():return back_btn("go_home","🏠 𝐇𝐨𝐦𝐞")
def bot_action_kb(bid,running=False):
    m=types.InlineKeyboardMarkup(row_width=2)
    if running:m.add(_btn("🛑 𝐒𝐭𝐨𝐩 𝐁𝐨𝐭", "bot_stop:"+str(bid)))
    else:m.add(_btn("▶️ 𝐒𝐭𝐚𝐫𝐭 𝐍𝐨𝐰", "project_start_page:"+str(bid)))
    m.add(_btn("📜 𝐕𝐢𝐞𝐰 𝐋𝐨𝐠𝐬", "bot_logs:"+str(bid)),_btn("🗑️ 𝐃𝐞𝐥𝐞𝐭𝐞", "bot_confirm_del:"+str(bid)))
    m.add(_btn("⬅️ 𝐌𝐲 𝐏𝐫𝐨𝐣𝐞𝐜𝐭𝐬", "menu_mybots"));return m

def plan_kb(plans=None):
    from config import PLAN_LIMITS
    m=types.InlineKeyboardMarkup(row_width=1)
    icons={'starter':'🌱','weekly':'⚡','fortnight':'🔥','monthly':'🌟','quarterly':'💠','halfyear':'🚀','yearly':'🏆','lifetime':'👑'}
    for k,p in (plans or PLAN_LIMITS).items():
        if k=='free':
            continue
        days=int(p.get('duration_days', 0) or 0)
        term='Lifetime' if days == 0 else (f'{days} Days' if days < 30 else (f'{days // 30} Months' if days % 30 == 0 and days < 365 else ('1 Year' if days == 365 else f'{days} Days')))
        m.add(_btn(f"{icons.get(k,'💎')} {p.get('name',k)} · {term} · ৳{p.get('price',0)}",f"plan_select:{k}"))
    m.add(_btn("🏠 𝐁𝐚𝐜𝐤 𝐓𝐨 𝐌𝐞𝐧𝐮","go_home"))
    return m

def pay_method_kb(plan):
    # Three supported checkout choices: apply a promo, spend wallet coins, or Telegram Stars.
    m=types.InlineKeyboardMarkup(row_width=1)
    m.add(_btn("🎟 𝐏𝐫𝐨𝐦𝐨 𝐂𝐨𝐝𝐞", f"promo_apply:{plan}"))
    m.add(_btn("🪙 𝐏𝐚𝐲 𝐖𝐢𝐭𝐡 𝐂𝐨𝐢𝐧𝐬", f"pay_wallet:{plan}"))
    m.add(_btn("⭐ 𝐏𝐚𝐲 𝐖𝐢𝐭𝐡 𝐓𝐞𝐥𝐞𝐠𝐫𝐚𝐦 𝐒𝐭𝐚𝐫𝐬", f"pay_stars:{plan}"))
    m.add(_btn("⬅️ 𝐁𝐚𝐜𝐤 𝐓𝐨 𝐏𝐥𝐚𝐧𝐬", "menu_sub"))
    return m

def admin_kb(uid):
    from core.state import state
    m=types.InlineKeyboardMarkup(row_width=2)
    rows=[
      (_btn("𝐔𝐬𝐞𝐫𝐬","adm_users"),_btn("𝐔𝐬𝐞𝐫 𝐒𝐞𝐚𝐫𝐜𝐡","adm_userinfo")),
      (_btn("𝐏𝐚𝐲𝐦𝐞𝐧𝐭𝐬","adm_payments"),_btn("𝐀𝐝𝐝 𝐒𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧","adm_addsub")),
      (_btn("𝐑𝐞𝐦𝐨𝐯𝐞 𝐒𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧","adm_remsub"),_btn("𝐀𝐝𝐝 𝐁𝐚𝐥𝐚𝐧𝐜𝐞","adm_give")),
      (_btn("𝐁𝐚𝐧 𝐔𝐬𝐞𝐫","adm_ban"),_btn("𝐔𝐧𝐛𝐚𝐧 𝐔𝐬𝐞𝐫","adm_unban")),
      (_btn("𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭","adm_broadcast"),_btn("𝐍𝐨𝐭𝐢𝐟𝐲","adm_notify")),
      (_btn("𝐂𝐡𝐚𝐧𝐧𝐞𝐥𝐬","adm_channels"),_btn("𝐓𝐢𝐜𝐤𝐞𝐭𝐬","adm_tickets")),
      (_btn("𝐏𝐫𝐨𝐦𝐨 𝐂𝐨𝐝𝐞𝐬","adm_promo"),_btn("🎟 𝐑𝐞𝐝𝐞𝐞𝐦 𝐂𝐨𝐝𝐞𝐬","adm_redeem")),
      (_btn("𝐒𝐲𝐬𝐭𝐞𝐦 𝐒𝐭𝐚𝐭𝐬","adm_system"),_btn("𝐀𝐝𝐦𝐢𝐧 𝐒𝐭𝐚𝐭𝐬","adm_stats")),
      (_btn("𝐔𝐬𝐞𝐫 𝐅𝐢𝐥𝐞𝐬","adm_userfiles"),_btn("𝐑𝐮𝐧𝐧𝐢𝐧𝐠 𝐔𝐬𝐞𝐫 𝐅𝐢𝐥𝐞𝐬","adm_runningfiles")),
      (_btn("𝐁𝐚𝐜𝐤𝐮𝐩","adm_backup"),_btn("𝐋𝐨𝐠𝐬","adm_logs")),
      (_btn("𝐂𝐥𝐞𝐚𝐧𝐮𝐩","adm_cleanup"),_btn("𝐒𝐭𝐨𝐩 𝐀𝐥𝐥 𝐁𝐨𝐭𝐬","adm_stopall")),
      (_btn("𝐅𝐨𝐫𝐜𝐞 𝐉𝐨𝐢𝐧: "+("𝐎𝐍" if state.force_sub_enabled else "𝐎𝐅𝐅"),"adm_fsub_toggle"),
       _btn("𝐁𝐨𝐭 𝐋𝐨𝐜𝐤: "+("𝐎𝐍" if state.bot_locked else "𝐎𝐅𝐅"),"adm_lock_toggle")),
      (_btn("𝐇𝐨𝐦𝐞","go_home"),_btn("𝐑𝐞𝐟𝐫𝐞𝐬𝐡","menu_admin"))
    ]
    for row in rows:m.row(*row)
    if int(uid)==int(__import__("config").OWNER_ID):
        m.add(_btn("𝐎𝐰𝐧𝐞𝐫 𝐒𝐞𝐭𝐭𝐢𝐧𝐠𝐬","owner_admin_help"))
    return m
def pay_approve_kb(pid):
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(_btn("𝐀𝐩𝐩𝐫𝐨𝐯𝐞",f"pay_approve:{pid}"),_btn("𝐑𝐞𝐣𝐞𝐜𝐭",f"pay_reject:{pid}"))
    return m
def channels_manage_kb(channels):
    m=types.InlineKeyboardMarkup(row_width=2)
    m.row(_btn("➕ Add Channel", "ch_add_channel"), _btn("➕ Add Group", "ch_add_group"))
    m.add(_btn("🔄 Force Join ON/OFF", "fsub_master_toggle"))
    for c in channels:
        key=c.get('channel_id', c.get('channel_username'))
        title=c.get('channel_name') or c.get('channel_username') or 'Chat'
        m.add(_btn(("🟢 " if c.get('is_active') else "🔴 ")+str(title)[:30],f"ch_toggle:{key}"))
    m.add(_btn("🗑 Remove Chat", "ch_remove"), _btn("⬅️ Back", "menu_admin"))
    return m
