# 07 — Discord Bots

Three separate services:
1. **Main Discord Bot** — Python, handles roles, voice rooms, welcome, verify
2. **SkinPeek** — Node.js, checks Valorant daily shop
3. **Bot Control API** — Flask, lets you restart/check bot status via HTTP

All three run as systemd services so they auto-start on boot.

---

## Create a Discord Bot Application

For each bot you want to run, go to https://discord.com/developers/applications:

1. New Application → give it a name
2. Bot → Add Bot → Copy Token (save it — only shown once)
3. Under Privileged Gateway Intents, enable:
   - Server Members Intent ✅
   - Message Content Intent ✅
   - Presence Intent ✅ (optional)
4. OAuth2 → URL Generator → Scopes: `bot`, `applications.commands`
5. Bot Permissions: `Administrator` (or fine-tune as needed)
6. Copy the generated URL and open it to invite the bot to your server

---

## Part 1 — Main Discord Bot (Python)

### 1. Clone / Copy the Bot Files

```bash
mkdir -p ~/bots/discord-bot
cd ~/bots/discord-bot
# Copy bot.py and requirements.txt from this repo
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
nano .env
```

Fill in all IDs. To get channel/role/message IDs in Discord:
- Settings → Advanced → Enable Developer Mode
- Right-click any server/channel/role/message → Copy ID

### 4. Set Up Reaction Roles Message

In your roles channel, post a message that lists games with emojis, e.g.:
```
React to get your game roles:
🎮 Valorant
⚔️ League of Legends
🎯 CS2
...
```

After posting, right-click → Copy Message ID → paste into `.env` as `REACTION_ROLES_MESSAGE_ID`.

### 5. Set Up Verify Message

In your verify channel, post a message like:
```
React with ✅ to verify and gain access to the server.
```

Copy its Message ID → paste into `.env` as `VERIFY_MESSAGE_ID`.

### 6. Install and Enable the Systemd Service

```bash
# Copy the service file
sudo cp ~/homelab-server/systemd/discordbot.service /etc/systemd/system/

# Edit it to match your actual username and paths
sudo nano /etc/systemd/system/discordbot.service

# Reload systemd, enable, and start
sudo systemctl daemon-reload
sudo systemctl enable discordbot
sudo systemctl start discordbot
sudo systemctl status discordbot
```

### 7. Monitor Logs

```bash
sudo journalctl -u discordbot -f
```

---

## Part 2 — SkinPeek (Valorant Skin Checker)

SkinPeek is an existing open-source Node.js bot.

### 1. Clone the Repo

```bash
cd ~
git clone https://github.com/giorgi-o/SkinPeek.git
cd SkinPeek
npm install
```

### 2. Configure SkinPeek

Follow the configuration guide in the SkinPeek repository README.
You'll need to provide your Discord bot token in the `config.json` file.

### 3. Riot Cookie Authentication

SkinPeek uses Riot Auth cookies for VALORANT store access.
Cookies expire periodically and must be refreshed.

Cookies needed (from `auth.riotgames.com` in your browser's DevTools):
- `ssid`
- `tdid`
- `sub`
- `csid`
- `clid`

In Discord, use the `/cookies` command and paste each value when prompted.

### 4. Install and Enable the Systemd Service

```bash
sudo cp ~/homelab-server/systemd/skinpeek.service /etc/systemd/system/

# Edit paths to match your setup
sudo nano /etc/systemd/system/skinpeek.service

sudo systemctl daemon-reload
sudo systemctl enable skinpeek
sudo systemctl start skinpeek
sudo systemctl status skinpeek
```

---

## Part 3 — Bot Control API (Flask)

This is a small REST API that lets you check bot status and restart them
via HTTP — useful for Homepage dashboard widgets.

### 1. Set Up the Flask App

```bash
mkdir -p ~/bots/bot-control
cd ~/bots/bot-control
# Copy app.py and requirements.txt from this repo

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

### 2. Install and Enable the Systemd Service

```bash
sudo cp ~/homelab-server/systemd/bot-control.service /etc/systemd/system/

# Edit paths to match your setup
sudo nano /etc/systemd/system/bot-control.service

sudo systemctl daemon-reload
sudo systemctl enable bot-control
sudo systemctl start bot-control
sudo systemctl status bot-control
```

### 3. Test the API

```bash
# Check status of all bots
curl http://localhost:9999/status

# Restart the main discord bot
curl -X POST http://localhost:9999/restart/discordbot

# Restart SkinPeek
curl -X POST http://localhost:9999/restart/skinpeek
```

Expected response:
```json
{"discordbot": "active", "skinpeek": "active"}
```

---

## Systemd Quick Reference

```bash
# Check all bot services at once
systemctl status discordbot skinpeek bot-control

# View live logs
sudo journalctl -u discordbot -f
sudo journalctl -u skinpeek -f
sudo journalctl -u bot-control -f

# Restart a bot manually
sudo systemctl restart discordbot

# Check if a service is enabled on boot
systemctl is-enabled discordbot
```
