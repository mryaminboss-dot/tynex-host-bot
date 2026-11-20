𝐓𝐘𝐍𝐄𝐗 𝐕𝐏𝐒 𝐒𝐄𝐑𝐕𝐄𝐑 — PROJECT NOTES

SETUP
1. Set BOT_TOKEN as an environment variable using a NEW token created in BotFather. Never place a bot token in a shared ZIP.
2. OWNER_ID is preserved as 8017553129. Change it only if the owner account itself changes.
3. BOT_USERNAME is currently set to TynexVPSBot. Make sure this matches the username actually assigned in BotFather.
4. Upload this ZIP through your existing Hosting Bot's project-upload option. Do not deploy this ZIP to Render for the workflow requested.
5. The hosting service must install packages from requirements.txt and start main.py.

ADMIN
- The configured owner can open the Admin Panel from the main menu.
- Additional admins can be managed by the owner with /addadmin TELEGRAM_ID and /deladmin TELEGRAM_ID.
- Owner contact shown to users: @MrTripleR_YT.

IMPORTANT
- The old token was exposed in a previous shared archive. Revoke it in BotFather and use a NEW token.
- MongoDB connection settings are optional; without a working MONGO_URL the application falls back to SQLite.
- SQLite data may not persist if the hosting provider uses temporary storage.
- Uploaded bot code runs as a child process under the same hosting account. This is not a security sandbox; only accept projects you trust.
- This archive has passed Python syntax compilation and ZIP integrity checks. A live Telegram test still requires a valid new token and the target hosting service.

SUBSCRIPTION PLANS
Plans are configured in config.py -> PLAN_LIMITS. Defaults include 3 days, 7 days,
15 days, 30 days, 3 months, 6 months, 1 year and lifetime. Change the `price`,
`max_bots`, `ram`, and `duration_days` values there to suit your service.
Users can purchase through the configured checkout options. Admins can grant or remove plans in
Admin Panel -> Add Subscription / Remove Subscription. Enter 0 days for lifetime.


PAYMENT UPDATE: Checkout options are Promo Code, Wallet Coins, and Telegram Stars (XTR). Referral reward is 10 wallet coins per successful referral. Telegram Stars rate is configured by STAR_PER_BDT in config.py. External bKash/Nagad/Rocket/manual payment methods are disabled in the current checkout.


UPLOAD SECURITY & ADMIN FILE MANAGEMENT
- Uploaded ZIP and single files are checked by security_scanner.py using static text/code analysis. The scanner does not execute uploaded code.
- Strong credential-exfiltration, obfuscated remote execution, and hosting-panel/server indicators are rejected. Other files that pass the heuristic scan are accepted automatically.
- Static scanning is heuristic, not a guarantee that a project is harmless. Approved user projects still run under the same OS account as the hosting service; use OS/container isolation and resource limits for production.
- Admin Panel -> User Files shows paginated upload records, uploader ID, upload number, file size, approval/rejection status, scan reason, and a download action.
- Admin Panel -> Running User Files lists deployed projects with Start/Stop, Logs, and Download controls, with pagination.
- No separate review bot or admin approval chat is used.
- The coin checkout displays required, available, and missing coin amounts when the balance is insufficient.

UPLOAD RETENTION UPDATE: Uploaded source files are archived under upload_bots/_user_uploads/<user_id>/ and remain available in Admin Panel -> User Files. Re-uploading a ZIP with the same filename creates a separate project folder and never deletes the previous project. Uploads are auto-approved after the static security scan; they are not auto-started.
