import os
import discord
from discord.ext import commands
from discord import app_commands

# ✅ Read the token from the correct environment variable
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("❌ DISCORD_TOKEN environment variable is missing!")

# ✅ Set bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

# ✅ Initialize bot
bot = commands.Bot(command_prefix="!", intents=intents)

# ✅ Sync commands to the guild only (faster, avoids global cooldown)
GUILD_ID = None  # Set your server ID here if you want faster command sync

@bot.event
async def on_ready():
    guild = None
    if GUILD_ID:
        guild = discord.Object(id=GUILD_ID)
    try:
        synced = await bot.tree.sync(guild=guild) if guild else await bot.tree.sync()
        print(f"✅ Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

# ✅ Basic slash command: /ping
@bot.tree.command(name="ping", description="Check if ARIA is alive.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong! ARIA is online and responsive.")

# ✅ Basic slash command: /info
@bot.tree.command(name="info", description="Get basic info about ARIA.")
async def info(interaction: discord.Interaction):
    await interaction.response.send_message(f"🤖 ARIA is active as {bot.user}!")

# ✅ Basic slash command: /sync (admin use only)
@bot.tree.command(name="sync", description="Force sync slash commands.")
async def sync_commands(interaction: discord.Interaction):
    try:
        synced = await bot.tree.sync()
        await interaction.response.send_message(f"✅ Synced {len(synced)} command(s).")
    except Exception as e:
        await interaction.response.send_message(f"❌ Sync failed: {e}")

# ✅ Run the bot
bot.run(TOKEN)