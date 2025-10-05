# Aria — Discord Bot (V1) • GitHub → Railway (Worker)

This repo is ready to deploy on **Railway** as a **Worker** process (no web server needed).

## What’s included
- `bot.py` — owner-locked slash commands, safe setup
- `requirements.txt` — pinned deps
- `server_structure.json` — channel/role template
- `Procfile` — defines worker start command

## Deploy on Railway (3–5 minutes)

1) **Create a Discord bot** in the Developer Portal
   - Reset/copy token
   - Turn on **SERVER MEMBERS INTENT** (and optionally MESSAGE CONTENT INTENT)
   - OAuth2 URL: check `bot` and `applications.commands`
   - Temporary permission: **Administrator** (can reduce later)

2) **Connect GitHub repo to Railway**
   - Railway → **New Project** → **Deploy from GitHub** → select this repo

3) **Set Environment Variables** in Railway → Variables
   - `DISCORD_TOKEN` = your bot token
   - `OWNER_ID` = your Discord user ID (e.g. 587806838716891147)

4) **Deploy**
   - Railway installs deps from `requirements.txt`
   - Starts worker using `Procfile`
   - Logs show: “Logged in as ...” and “Synced X command(s).”

5) **In your Discord server**
   - Run `/ping` (sanity)
   - Run `/create_roles`
   - Run `/setup_server`

---

## Notes
- All sensitive commands are **owner-only** (checked against `OWNER_ID`).
- Edit `server_structure.json` to tweak categories/channels; re-run `/setup_server`.
- Add new commands and run `/sync_commands` to refresh slash commands.