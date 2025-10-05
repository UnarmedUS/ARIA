import os
import random
import asyncio
import logging
import discord
from discord import app_commands
from discord.ext import commands

# -------- Logging --------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
log = logging.getLogger("aria")

# -------- Config --------
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("❌ TOKEN environment variable is missing!")

# Optional: fast dev sync to one server (paste your guild ID as an env var)
GUILD_ID = os.getenv("GUILD_ID")
GUILD = discord.Object(int(GUILD_ID)) if GUILD_ID else None

# Use only safe, non-privileged intents (no members/presence/message_content)
intents = discord.Intents.none()
# Slash commands don’t need message content intent
bot = commands.Bot(command_prefix="!", intents=intents)

# -------- Slash Commands --------
@bot.tree.command(description="Check if ARIA is alive.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong! ARIA is online.", ephemeral=True)

@bot.tree.command(description="What can ARIA do right now?")
async def help(interaction: discord.Interaction):
    msg = (
        "**A.R.I.A. v1 — available commands**\n"
        "• `/ping` — basic health check\n"
        "• `/tip` — quick CoD tip\n"
        "• `/about` — bot info\n"
        "\n*More coming once we stabilize deployment.*"
    )
    await interaction.response.send_message(msg, ephemeral=True)

COD_TIPS = [
    "Center your crosshair at head/upper-chest level while moving.",
    "Slide-cancel is gone in some titles — learn the current tax of movement.",
    "Pre-aim common angles; don’t hard-scope your sprint-out.",
    "Use audio intel: walk unless you need to sprint.",
    "Break cameras by changing elevation with jumps/ledge mantles.",
    "Plate in cover; don’t re-peek instantly after plating.",
    "Use stims/smokes to disengage, not only to push.",
    "Trade kills: push in pairs when possible.",
    "Reset fights — armor/reload before re-challenging.",
    "Don’t loot in the open; clear the area first."
]

@bot.tree.command(description="Get a quick CoD tip.")
async def tip(interaction: discord.Interaction):
    await interaction.response.send_message(f"💡 {random.choice(COD_TIPS)}", ephemeral=True)

@bot.tree.command(description="About ARIA.")
async def about(interaction: discord.Interaction):
    app = bot.user
    await interaction.response.send_message(
        f"🤖 **A.R.I.A.** — your Call of Duty coaching assistant.\n"
        f"User: {app} | ID: `{bot.user.id}`\n"
        f"Guild-scoped sync: {'Yes' if GUILD else 'No (global)'}.",
        ephemeral=True
    )

# Owner-only manual sync (handy if commands ever get stuck)
@commands.is_owner()
@bot.tree.command(description="Owner: force re-sync commands.")
async def sync(interaction: discord.Interaction):
    try:
        if GUILD:
            synced = await bot.tree.sync(guild=GUILD)
            await interaction.response.send_message(f"🔁 Synced {len(synced)} command(s) to guild.", ephemeral=True)
        else:
            synced = await bot.tree.sync()
            await interaction.response.send_message(f"🔁 Synced {len(synced)} global command(s).", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Sync failed: `{e}`", ephemeral=True)

# -------- Lifecycle --------
@bot.event
async def on_ready():
    try:
        if GUILD:
            bot.tree.copy_global_to(guild=GUILD)
            synced = await bot.tree.sync(guild=GUILD)
            log.info("✅ Logged in as %s (%s) • Synced %d command(s) to guild %s",
                     bot.user, bot.user.id, len(synced), GUILD.id)
        else:
            synced = await bot.tree.sync()
            log.info("✅ Logged in as %s (%s) • Synced %d global command(s)",
                     bot.user, bot.user.id, len(synced))
    except Exception as e:
        log.exception("Command sync failed: %s", e)

bot.run(TOKEN)