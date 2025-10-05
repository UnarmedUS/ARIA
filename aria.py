import os
import json
import discord
from discord.ext import commands
from discord import app_commands

# =========================
# INTENTS
# =========================
intents = discord.Intents.default()
intents.guilds = True
intents.members = True          # enable "Server Members Intent" in Dev Portal
intents.message_content = True  # required for on_message content access

# =========================
# CONFIG / ENV
# =========================
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("❌ DISCORD_TOKEN environment variable is missing!")

# Optional: your owner ID (used in logs/owner pings later if desired)
OWNER_ID = 587806838716891147  # provided earlier

# =========================
# BOT
# =========================
bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# DATA LAYER
# =========================
DATA_FOLDER   = "data"
USERS_FILE    = f"{DATA_FOLDER}/users.json"
SERVERS_FILE  = f"{DATA_FOLDER}/servers.json"
LOGS_FILE     = f"{DATA_FOLDER}/logs.json"

def ensure_data_files():
    os.makedirs(DATA_FOLDER, exist_ok=True)
    for file in [USERS_FILE, SERVERS_FILE, LOGS_FILE]:
        if not os.path.exists(file):
            with open(file, "w", encoding="utf-8") as f:
                json.dump({}, f)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

ensure_data_files()

# =========================
# UTIL
# =========================
def get_server_settings(guild: discord.Guild):
    data = load_json(SERVERS_FILE)
    gid = str(guild.id)
    if gid not in data:
        data[gid] = {
            "server_name": guild.name,
            "settings": {
                # sensible defaults
                "welcome_enabled": "false",
                "welcome_channel_id": ""  # optional fixed channel
            }
        }
        save_json(SERVERS_FILE, data)
    return data

def set_server_setting(guild: discord.Guild, key: str, value: str):
    data = get_server_settings(guild)
    gid = str(guild.id)
    data[gid]["settings"][key] = value
    save_json(SERVERS_FILE, data)

def get_user_profile(user: discord.abc.User):
    data = load_json(USERS_FILE)
    uid = str(user.id)
    if uid not in data:
        data[uid] = {"username": user.name, "settings": {}}
        save_json(USERS_FILE, data)
    return data

def set_user_setting(user: discord.abc.User, key: str, value: str):
    data = get_user_profile(user)
    uid = str(user.id)
    data[uid]["settings"][key] = value
    save_json(USERS_FILE, data)

# =========================
# EVENTS
# =========================
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"✅ Slash commands synced: {len(synced)}")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

@bot.event
async def on_guild_join(guild: discord.Guild):
    # Initialize server settings and log
    settings = get_server_settings(guild)
    logs = load_json(LOGS_FILE)
    logs.setdefault("guild_joins", [])
    logs["guild_joins"].append({"guild_id": guild.id, "guild_name": guild.name})
    save_json(LOGS_FILE, logs)

    # Find a channel to greet (prefer system or first text)
    channel = guild.system_channel
    if channel is None:
        for c in guild.text_channels:
            if c.permissions_for(guild.me).send_messages:
                channel = c
                break

    if channel:
        try:
            await channel.send(
                f"👋 Hi everyone, I’m **ARIA**! Thanks for inviting me to **{guild.name}**.\n"
                "Use `/about` and `/help` to see what I can do.\n"
                "Admins can configure me with `/settings`."
            )
        except Exception:
            pass

@bot.event
async def on_member_join(member: discord.Member):
    # Respect server setting
    data = get_server_settings(member.guild)
    s = data[str(member.guild.id)]["settings"]
    welcome_enabled = s.get("welcome_enabled", "false").lower() == "true"
    if not welcome_enabled:
        return

    channel_id = s.get("welcome_channel_id") or ""
    channel = None
    if channel_id.isdigit():
        channel = member.guild.get_channel(int(channel_id))
    if channel is None:
        channel = member.guild.system_channel or next(
            (c for c in member.guild.text_channels if c.permissions_for(member.guild.me).send_messages),
            None
        )

    if channel:
        try:
            await channel.send(f"🎉 Welcome {member.mention}! I’m ARIA — try `/introduce` to meet me.")
        except Exception:
            pass

@bot.event
async def on_message(message: discord.Message):
    # Ignore self
    if message.author.bot:
        return

    # If ARIA is mentioned, give a friendly pointer
    if bot.user in message.mentions:
        try:
            await message.channel.send(
                "👋 I’m here! Try `/help` for commands, or `/introduce` to learn what I can do in this server."
            )
        except Exception:
            pass

    # Important: let commands still run
    await bot.process_commands(message)

# =========================
# CORE SLASH COMMANDS
# =========================
@bot.tree.command(name="ping", description="Check if the bot is responsive.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong! I'm awake.", ephemeral=True)

@bot.tree.command(name="about", description="Learn more about the bot.")
async def about(interaction: discord.Interaction):
    msg = (
        "**🤖 ARIA** — Adaptive, Responsive, Intelligent Assistant\n"
        "Built for coaching, coordination, and interaction across Discord.\n"
        "Core: Interaction & Awareness layer online."
    )
    await interaction.response.send_message(msg, ephemeral=True)

@bot.tree.command(name="help", description="Show available commands.")
async def help_cmd(interaction: discord.Interaction):
    commands_list = [
        "`/ping` — Check responsiveness",
        "`/about` — Info about ARIA",
        "`/help` — This list",
        "`/introduce` — ARIA introduces herself based on context",
        "`/profile [field] [value]` — Set your personal options",
        "`/settings [field] [value]` — Server config (admins)",
        "`/report <message>` — Send feedback/issues"
    ]
    msg = "**Available Commands:**\n" + "\n".join(commands_list)
    await interaction.response.send_message(msg, ephemeral=True)

# =========================
# INTRODUCE (Context-aware)
# =========================
@bot.tree.command(name="introduce", description="ARIA introduces herself based on context.")
async def introduce(interaction: discord.Interaction):
    in_dm = interaction.guild is None
    user = interaction.user

    if in_dm:
        msg = (
            f"Hey {user.mention}! I’m **ARIA** — your assistant. "
            "From DMs I can help you with personal settings and guidance. "
            "Invite me to a server to enable coaching tools, coordination and accountability features."
        )
        await interaction.response.send_message(msg, ephemeral=True)
        return

    guild = interaction.guild
    settings = get_server_settings(guild)
    s = settings[str(guild.id)]["settings"]
    welcome_status = "on ✅" if s.get("welcome_enabled", "false").lower() == "true" else "off ❌"

    msg = (
        f"Hello **{guild.name}**! I’m **ARIA**.\n"
        "• I help with coaching, coordination, and healthy community interactions.\n"
        "• Try `/help` to see what’s available now.\n"
        "• Admins: `/settings welcome_enabled true/false` (currently **"
        f"{welcome_status}**). Optionally set `welcome_channel_id`."
    )
    await interaction.response.send_message(msg, ephemeral=True)

# =========================
# SETTINGS (Server)
# =========================
@bot.tree.command(name="settings", description="View or change server settings.")
@app_commands.describe(
    field="The setting name to change (optional)",
    value="The new value (optional)"
)
async def settings_cmd(interaction: discord.Interaction, field: str = None, value: str = None):
    if interaction.guild is None:
        await interaction.response.send_message("This command must be used in a server.", ephemeral=True)
        return

    # Optional: check for manage_guild permission for changes
    can_manage = interaction.user.guild_permissions.manage_guild

    data = get_server_settings(interaction.guild)
    gid = str(interaction.guild.id)

    if field is None and value is None:
        current = data[gid]["settings"]
        if not current:
            msg = "No custom settings found for this server."
        else:
            lines = [f"**{k}**: {v}" for k, v in current.items()]
            msg = "**Current Server Settings:**\n" + "\n".join(lines)
        await interaction.response.send_message(msg, ephemeral=True)
        return

    if not can_manage:
        await interaction.response.send_message(
            "You need the **Manage Server** permission to change settings.",
            ephemeral=True
        )
        return

    if field and value:
        set_server_setting(interaction.guild, field, value)
        await interaction.response.send_message(
            f"✅ Setting **{field}** updated to **{value}**.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "To update a setting, provide both a field and a value.",
            ephemeral=True
        )

# =========================
# PROFILE (User)
# =========================
@bot.tree.command(name="profile", description="View or update your personal settings.")
@app_commands.describe(
    field="The setting name to update (optional)",
    value="The new value (optional)"
)
async def profile_cmd(interaction: discord.Interaction, field: str = None, value: str = None):
    user = interaction.user
    data = get_user_profile(user)
    uid = str(user.id)

    if field is None and value is None:
        current = data[uid]["settings"]
        if not current:
            msg = "You don't have any custom settings yet."
        else:
            lines = [f"**{k}**: {v}" for k, v in current.items()]
            msg = "**Your Profile Settings:**\n" + "\n".join(lines)
        await interaction.response.send_message(msg, ephemeral=True)
        return

    if field and value:
        set_user_setting(user, field, value)
        await interaction.response.send_message(
            f"✅ Your setting **{field}** is now **{value}**.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "To update a setting, provide both a field and a value.",
            ephemeral=True
        )

# =========================
# REPORT
# =========================
@bot.tree.command(name="report", description="Send feedback, report an issue, or suggest improvements.")
@app_commands.describe(
    message="Describe the issue or feedback you want to report."
)
async def report_cmd(interaction: discord.Interaction, message: str):
    logs = load_json(LOGS_FILE)
    logs.setdefault("reports", [])
    logs["reports"].append({
        "user_id": interaction.user.id,
        "username": interaction.user.name,
        "guild_id": interaction.guild.id if interaction.guild else None,
        "message": message
    })
    save_json(LOGS_FILE, logs)

    await interaction.response.send_message(
        "✅ Your report has been recorded. Thank you!",
        ephemeral=True
    )

# =========================
# RUN
# =========================
bot.run(TOKEN)

