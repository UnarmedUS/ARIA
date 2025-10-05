import os
import json
import discord
from discord.ext import commands
from discord import app_commands

# ---------- INTENTS ----------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# ---------- TOKEN & OWNER ----------
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    # Fallback to TOKEN if the env var hasn't been updated yet
    TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("❌ DISCORD_TOKEN or TOKEN environment variable is missing!")

# Replace with your Discord user ID (as provided)
OWNER_ID = 587806838716891147

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# ---------- DATA FOLDER & HELPER FUNCTIONS ----------
DATA_FOLDER = "data"
USERS_FILE = f"{DATA_FOLDER}/users.json"
SERVERS_FILE = f"{DATA_FOLDER}/servers.json"
LOGS_FILE = f"{DATA_FOLDER}/logs.json"

def ensure_data_files():
    """Create data folder/files if missing."""
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)

    for file in [USERS_FILE, SERVERS_FILE, LOGS_FILE]:
        if not os.path.exists(file):
            with open(file, "w") as f:
                json.dump({}, f)

def load_json(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# ---------- BOT EVENTS ----------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    ensure_data_files()
    try:
        await bot.tree.sync()
        print("✅ Slash commands synced.")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")

# ---------- OWNER-ONLY SYNC COMMAND ----------
@bot.tree.command(name="sync", description="Manually sync slash commands (Owner only).")
async def sync_cmd(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "❌ You do not have permission to use this command.",
            ephemeral=True
        )
        return

    try:
        await bot.tree.sync()
        await interaction.response.send_message(
            "✅ Commands have been synced successfully!",
            ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(
            f"❌ Failed to sync commands: {e}",
            ephemeral=True
        )

# ---------- CORE SLASH COMMANDS ----------
@bot.tree.command(name="ping", description="Check if the bot is responsive.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong! I'm awake.", ephemeral=True)

@bot.tree.command(name="about", description="Learn more about the bot.")
async def about(interaction: discord.Interaction):
    msg = (
        "**🤖 ARIA** — Adaptive, Responsive, Intelligent Assistant\n"
        "Built for coaching, coordination, and interaction across Discord.\n"
        "Version: 1.0 (Core setup phase)"
    )
    await interaction.response.send_message(msg, ephemeral=True)

@bot.tree.command(name="help", description="Show available commands.")
async def help_cmd(interaction: discord.Interaction):
    commands_list = [
        "`/ping` - Check responsiveness",
        "`/about` - Info about the bot",
        "`/help` - Show this message",
        "`/profile` - User settings",
        "`/settings` - Server config",
        "`/report` - Send feedback/issues",
        "`/sync` - (Owner only)"
    ]
    msg = "**Available Commands:**\n" + "\n".join(commands_list)
    await interaction.response.send_message(msg, ephemeral=True)

# ---------- SERVER SETTINGS COMMAND ----------
@bot.tree.command(name="settings", description="View or change server settings.")
@app_commands.describe(
    field="The setting name to change (optional)",
    value="The new value (optional)"
)
async def settings(interaction: discord.Interaction, field: str = None, value: str = None):
    guild_id = str(interaction.guild.id)
    data = load_json(SERVERS_FILE)

    # Create server entry if missing
    if guild_id not in data:
        data[guild_id] = {
            "server_name": interaction.guild.name,
            "settings": {}
        }
        save_json(SERVERS_FILE, data)

    # If no args, show the current settings
    if field is None and value is None:
        current = data[guild_id]["settings"]
        if not current:
            msg = "No custom settings found for this server."
        else:
            lines = [f"**{k}**: {v}" for k, v in current.items()]
            msg = "**Current Server Settings:**\n" + "\n".join(lines)
        await interaction.response.send_message(msg, ephemeral=True)
        return

    # If both field & value provided, update the setting
    if field and value:
        data[guild_id]["settings"][field] = value
        save_json(SERVERS_FILE, data)
        msg = f"✅ Setting **{field}** updated to **{value}**."
        await interaction.response.send_message(msg, ephemeral=True)
    else:
        await interaction.response.send_message(
            "To update a setting, provide both a field and a value.",
            ephemeral=True
        )

# ---------- USER PROFILE COMMAND ----------
@bot.tree.command(name="profile", description="View or update your personal settings.")
@app_commands.describe(
    field="The setting name to update (optional)",
    value="The new value (optional)"
)
async def profile(interaction: discord.Interaction, field: str = None, value: str = None):
    user_id = str(interaction.user.id)
    data = load_json(USERS_FILE)

    # Create user entry if missing
    if user_id not in data:
        data[user_id] = {
            "username": interaction.user.name,
            "settings": {}
        }
        save_json(USERS_FILE, data)

    # If no args, show current profile settings
    if field is None and value is None:
        current = data[user_id]["settings"]
        if not current:
            msg = "You don't have any custom settings yet."
        else:
            lines = [f"**{k}**: {v}" for k, v in current.items()]
            msg = "**Your Profile Settings:**\n" + "\n".join(lines)
        await interaction.response.send_message(msg, ephemeral=True)
        return

    # If both field and value provided, update
    if field and value:
        data[user_id]["settings"][field] = value
        save_json(USERS_FILE, data)
        msg = f"✅ Your setting **{field}** is now **{value}**."
        await interaction.response.send_message(msg, ephemeral=True)
    else:
        await interaction.response.send_message(
            "To update a setting, provide both a field and a value.",
            ephemeral=True
        )

# ---------- REPORT COMMAND ----------
@bot.tree.command(name="report", description="Send feedback, report an issue, or suggest improvements.")
@app_commands.describe(
    message="Describe the issue or feedback you want to report."
)
async def report(interaction: discord.Interaction, message: str):
    user_id = str(interaction.user.id)
    logs = load_json(LOGS_FILE)

    # Create user log list if absent
    if user_id not in logs:
        logs[user_id] = []

    # Append the report
    logs[user_id].append({
        "username": interaction.user.name,
        "message": message
    })
    save_json(LOGS_FILE, logs)

    await interaction.response.send_message(
        "✅ Your report has been recorded. Thank you!",
        ephemeral=True
    )

# ---------- RUN THE BOT ----------
bot.run(TOKEN)