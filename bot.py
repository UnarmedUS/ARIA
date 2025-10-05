import os
import discord
from discord.ext import commands
from discord import app_commands

# Get token from environment (Railway)
TOKEN = os.getenv("DISCORD_TOKEN")

# Set up basic intents
intents = discord.Intents.default()
intents.message_content = True  # Only needed if you plan to read messages

# Create bot instance
bot = commands.Bot(command_prefix="!", intents=intents)

# Example slash command
@bot.tree.command(name="ping", description="Check if the bot is responding")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

# You can add more slash commands here the same way:
# @bot.tree.command(name="hello", description="Says hello!")
# async def hello(interaction: discord.Interaction):
#     await interaction.response.send_message("Hello!")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Error syncing commands: {e}")

if __name__ == "__main__":
    if not TOKEN:
        raise ValueError("DISCORD_TOKEN environment variable not set.")
    bot.run(TOKEN)