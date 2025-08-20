# Price Monitor Bot

## Setup:

1. **Create Telegram Bot:**
   - Message @BotFather on Telegram
   - Send `/newbot`
   - Get your bot token

2. **Get Chat ID:**
   - Message @userinfobot
   - Copy your chat ID

3. **GitHub Setup:**
   - Push this repo to GitHub
   - Go to Settings → Secrets → Actions
   - Add `BOT_TOKEN` and `CHAT_ID`

4. **Customize:**
   - Edit `monitor.py` line 11: Replace with your product URL
   - Test: Actions → Price Monitor → Run workflow

**Runs every 6 hours automatically!**