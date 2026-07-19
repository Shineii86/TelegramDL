# ❓ Frequently Asked Questions

## 📖 General

<details>
<summary><b>What is TelegramDL?</b></summary>

TelegramDL is a Telegram bot that downloads content from channels, groups, bots, and stories — including restricted content that normally can't be downloaded.
</details>

<details>
<summary><b>Is TelegramDL free?</b></summary>

Yes! TelegramDL is open-source and free to use. There's a free tier with daily limits (10 downloads/day, 2GB max file size). Premium plans offer unlimited access.
</details>

<details>
<summary><b>Is it safe? Will I get banned?</b></summary>

TelegramDL uses built-in delays (default 10s) to protect your account from rate limits. The bot handles public content via bot token, and only uses user session when absolutely necessary for restricted content.
</details>

<details>
<summary><b>Do I need to be a channel member?</b></summary>

For **public channels**: No, bot token works.
For **private/restricted channels**: Yes, you must be a member and use a session string.
</details>

---

## 🔐 Login & Sessions

<details>
<summary><b>What is a session string?</b></summary>

A session string is a serialized authentication token that allows the bot to act as you (the user) to access restricted content. It's like a password — **never share it**.
</details>

<details>
<summary><b>How do I generate a session string?</b></summary>

**Method 1: Using the Bot**
1. Send `/login` to the bot
2. Enter your phone number
3. Enter the OTP code
4. Copy the session string

**Method 2: Using Colab**
1. Open the Colab notebook
2. Run Step 4 (Session Generator)
3. Enter your credentials
4. Copy the session string to Step 2
</details>

<details>
<summary><b>What's LOGIN_SYSTEM?</b></summary>

- `LOGIN_SYSTEM=true` (Recommended): Each user authenticates with their own phone number. Everyone has their own session.
- `LOGIN_SYSTEM=false`: Uses a single global session (the admin's). All users share access.
</details>

<details>
<summary><b>My session expired. What do I do?</b></summary>

Generate a new session string using `/login` or the Colab session generator. Sessions can expire if Telegram detects unusual activity.
</details>

---

## 📥 Downloads

<details>
<summary><b>What links are supported?</b></summary>

| Format | Example |
|--------|---------|
| Public Channel | `https://t.me/durov/123` |
| Private Channel | `https://t.me/c/1234567890/123` |
| Story | `https://t.me/username/s/123` |
| Batch Range | `https://t.me/username/1001-1010` |
| Bot Chat | `https://t.me/b/botusername/123` |
| Group | `https://t.me/groupname/123` |
| Invite Link | `https://t.me/+invitehash` |
| Username | `durov` |
| Numeric ID | `-1003983952160/123` |
</details>

<details>
<summary><b>How do I batch download?</b></summary>

Send `/batch` followed by a message range URL:
```
/batch https://t.me/username/1001-1010
```
The bot will download all messages from 1001 to 1010.
</details>

<details>
<summary><b>Can I download from private channels?</b></summary>

Yes! You need:
1. To be a member of the channel
2. A valid session string (generate with `/login`)
3. Set `LOGIN_SYSTEM=true` in config
</details>

<details>
<summary><b>Can I download stories?</b></summary>

Yes! Send a story link:
```
https://t.me/username/s/123
```
Stories are downloaded as photos or videos.
</details>

<details>
<summary><b>Can I download from groups?</b></summary>

Yes! Send a group message link:
```
https://t.me/groupname/123
```
Works for both public and private groups (with session).
</details>

<details>
<summary><b>Can I download from bot chats?</b></summary>

Yes! Send a bot chat link:
```
https://t.me/b/botusername/123
```
You'll need a session string and the message ID (use Plus Messenger to find it).
</details>

<details>
<summary><b>What's the file size limit?</b></summary>

- **Free users**: 2GB max
- **Premium users**: 4GB max
- Files larger than 2GB are automatically split into 1.9GB parts.
</details>

---

## ⚙️ Configuration

<details>
<summary><b>Where do I get API_ID and API_HASH?</b></summary>

1. Go to [my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Go to "API Development Tools"
4. Create an application
5. Copy API_ID and API_HASH
</details>

<details>
<summary><b>What is BOT_TOKEN?</b></summary>

Create a bot with [@BotFather](https://t.me/BotFather) on Telegram:
1. Send `/newbot`
2. Choose a name and username
3. Copy the token (format: `123456:ABC-DEF...`)
</details>

<details>
<summary><b>What is CHANNEL_ID?</b></summary>

The channel ID for auto-uploading downloads. To get it:
1. Add your bot to the channel as admin
2. Send a message to the channel
3. Forward to [@userinfobot](https://t.me/userinfobot)
4. Copy the channel ID (format: `-1001234567890`)
</details>

<details>
<summary><b>What is ADMINS?</b></summary>

Your Telegram user ID (and other admins). To get it:
1. Send `/start` to the bot
2. Or use [@userinfobot](https://t.me/userinfobot)
3. Set as comma-separated IDs: `123456789,987654321`
</details>

<details>
<summary><b>What is WAITING_TIME?</b></summary>

The delay (in seconds) between downloading and uploading each file. Default: 10s. Increase if you get FloodWait errors.
</details>

---

## 🚀 Deployment

<details>
<summary><b>What's the easiest way to deploy?</b></summary>

**Google Colab** — Click the button, fill credentials, run. No installation needed.
</details>

<details>
<summary><b>Do I need MongoDB?</b></summary>

Only if `LOGIN_SYSTEM=true`. If `LOGIN_SYSTEM=false`, you can skip MongoDB and set `STRING_SESSION` directly.
</details>

<details>
<summary><b>How do I deploy on VPS?</b></summary>

```bash
git clone https://github.com/Shineii86/TelegramDL.git
cd TelegramDL
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env  # Fill credentials
python3 bot.py
```
</details>

<details>
<summary><b>How do I deploy with Docker?</b></summary>

```bash
docker build -t telegramdl .
docker run -d --name telegramdl \
  -e API_ID=your_api_id \
  -e API_HASH=your_api_hash \
  -e BOT_TOKEN=your_bot_token \
  telegramdl
```
</details>

---

## 💳 Premium

<details>
<summary><b>What are the premium benefits?</b></summary>

| Feature | Free | Premium |
|---------|------|---------|
| Daily Downloads | 10 | Unlimited |
| Max File Size | 2GB | 4GB |
| Custom Thumbnails | ❌ | ✅ |
| Custom Captions | ❌ | ✅ |
| Dump Chat | ❌ | ✅ |
| Priority Speed | ❌ | ✅ |
</details>

<details>
<summary><b>How do I get premium?</b></summary>

1. Send `/premium` to view plans
2. Choose a plan: `/pay monthly`
3. Make payment via UPI/PayPal/Crypto/Stars
4. Send proof to admin
5. Admin approves with `/approve <request_id>`
</details>

<details>
<summary><b>What payment methods are accepted?</b></summary>

- 💵 USDT (ByBit) — BSC/ERC20/TON
- 🪙 TON (Tonkeeper)
- 🇮🇳 INR PhonePe (UPI)
- ⭐️ Telegram Stars
</details>

---

## 🐛 Troubleshooting

<details>
<summary><b>"Channel is private" error</b></summary>

**Cause**: Bot doesn't have access to private channel.
**Solution**: Join the channel and use a session string.
</details>

<details>
<summary><b>"Session expired" error</b></summary>

**Cause**: Session string is invalid or expired.
**Solution**: Generate a new session string with `/login`.
</details>

<details>
<summary><b>"FloodWaitError" error</b></summary>

**Cause**: Too many requests in short time.
**Solution**: Increase `WAITING_TIME` in config (try 15-30 seconds).
</details>

<details>
<summary><b>"File too large" error</b></summary>

**Cause**: File exceeds size limit.
**Solution**: Increase `MAX_FILE_SIZE_MB` in config, or the file is too large for Telegram's 4GB limit.
</details>

<details>
<summary><b>"Login failed" error</b></summary>

**Cause**: Wrong API_ID or API_HASH.
**Solution**: Double-check credentials from [my.telegram.org](https://my.telegram.org).
</details>

<details>
<summary><b>Bot not responding</b></summary>

**Possible causes**:
1. Wrong BOT_TOKEN — verify with @BotFather
2. Bot not started — send `/start`
3. Network issues — check internet connection
4. FloodWait — wait for the specified time
</details>

<details>
<summary><b>Downloads failing</b></summary>

**Possible causes**:
1. Bot not a member of channel
2. Session expired — regenerate with `/login`
3. File too large — check `MAX_FILE_SIZE_MB`
4. Network timeout — increase `WAITING_TIME`
</details>

<details>
<summary><b>Colab disconnecting</b></summary>

**Solution**:
1. Enable `USE_CHECKPOINT=true` for resume
2. Enable `KEEP_ALIVE=true`
3. Use Colab Pro for longer sessions
4. Download to Google Drive for persistence
</details>

---

## 📞 Still Need Help?

- **GitHub Issues**: [Open an Issue](https://github.com/Shineii86/TelegramDL/issues)
- **Telegram**: [@Shineii86](https://t.me/Shineii86)
- **Email**: ikx7a@hotmail.com

---

**Last Updated**: 2026-01-19
