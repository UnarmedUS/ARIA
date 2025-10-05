import os
import discord
from discord.ext import commands
from discord import app_commands

# ✅ Intents (only what's needed)
intents = discord.Intents.default()
intents.message_content = False
intents.members = False
intents.presences = False

# ✅ Bot setup
bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None  # Disable default help
)

# ✅ Slash command tree
tree = bot.tree

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        await tree.sync()
        print("✅ Slash commands synced.")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

# ✅ /ping command
@tree.command(name="ping", description="Check if ARIA is online.")
async def ping_command(interaction: discord.Interaction):
    await interaction.response.send_message("Online and running.")

# ✅ /aria command
@tree.command(name="aria", description="Talk to ARIA.")
async def aria_command(interaction: discord.Interaction):
    await interaction.response.send_message("What do you need?")

# ✅ /hello command
@tree.command(name="hello", description="Say hello to ARIA.")
async def hello_command(interaction: discord.Interaction):
    await interaction.response.send_message("Hey. What’s up?")

# ✅ Load token from Railway environment variable
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("❌ TOKEN environment variable is missing!")

bot.run(TOKEN)