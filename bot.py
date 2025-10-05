import os
import discord
from discord.ext import commands
from discord import app_commands

# Get token from Railway environment variable
TOKEN = os.getenv("DISCORD_TOKEN")

# Set up bot intents
intents = discord.Intents.default()
intents.message_content = True  # Enable if message reading is needed

# Create the bot instance
bot = commands.Bot(command_prefix="!", intents=intents)

# --- Slash Commands ---

@bot.tree.command(name="ping", description="Check if the bot is responding")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

# --- Events ---

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")

# --- Run the Bot ---

if __name__ == "__main__":
    if not TOKEN:
        raise ValueError("❌ DISCORD_TOKEN environment variable not set.")
    bot.run(TOKEN)