import os
import json
import logging
import discord
from discord import app_commands
from discord.ext import commands

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True  # optional for future features

bot = commands.Bot(command_prefix="!", intents=intents)

def owner_only(interaction: discord.Interaction) -> bool:
    return interaction.user.id == OWNER_ID

async def deny_if_not_owner(interaction: discord.Interaction) -> bool:
    if not owner_only(interaction):
        try:
            await interaction.response.send_message(
                "Sorry, this command is owner-only for now.", ephemeral=True
            )
        except discord.InteractionResponded:
            await interaction.followup.send("Sorry, this command is owner-only for now.", ephemeral=True)
        return False
    return True

async def ensure_roles(guild: discord.Guild, structure: dict):
    role_colors = {
        "green": discord.Color.green(),
        "blue": discord.Color.blue(),
        "red": discord.Color.red(),
        "gold": discord.Color.gold()
    }
    for r in structure.get("roles", []):
        existing = discord.utils.get(guild.roles, name=r["name"])
        if existing:
            continue
        await guild.create_role(
            name=r["name"],
            colour=role_colors.get(r.get("color","blue"), discord.Color.blue()),
            hoist=r.get("hoist", True),
            mentionable=r.get("mentionable", True),
            reason="Aria setup: creating safeguard role"
        )

async def setup_structure(guild: discord.Guild, structure: dict):
    for cat in structure.get("categories", []):
        category = discord.utils.get(guild.categories, name=cat["name"])
        if category is None:
            category = await guild.create_category(cat["name"], reason="Aria setup: creating category")
        for name in cat.get("text_channels", []):
            ch = discord.utils.get(guild.text_channels, name=name)
            if ch is None:
                await guild.create_text_channel(name, category=category, reason="Aria setup: creating text channel")
        for name in cat.get("voice_channels", []):
            ch = discord.utils.get(guild.voice_channels, name=name)
            if ch is None:
                await guild.create_voice_channel(name, category=category, reason="Aria setup: creating voice channel")

@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        logging.info(f"Synced {len(synced)} command(s).")
    except Exception as e:
        logging.exception("Failed to sync commands: %s", e)

@bot.tree.command(description="Check if Aria is online (owner-only response).")
async def ping(interaction: discord.Interaction):
    if not await deny_if_not_owner(interaction): return
    await interaction.response.send_message("Pong. Aria is responsive and ready.", ephemeral=True)

@bot.tree.command(description="Create safeguard roles (Coach-Lead, Operations).")
async def create_roles(interaction: discord.Interaction):
    if not await deny_if_not_owner(interaction): return
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message("This must be used in a server.", ephemeral=True)
        return
    with open("server_structure.json", "r") as f:
        structure = json.load(f)
    await ensure_roles(guild, structure)
    await interaction.response.send_message("Roles verified/created.", ephemeral=True)

@bot.tree.command(description="Set up the server categories/channels from template.")
async def setup_server(interaction: discord.Interaction):
    if not await deny_if_not_owner(interaction): return
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message("This must be used in a server.", ephemeral=True)
        return
    with open("server_structure.json", "r") as f:
        structure = json.load(f)
    await ensure_roles(guild, structure)
    await setup_structure(guild, structure)
    await interaction.response.send_message("Server structure verified/created.", ephemeral=True)

@bot.tree.command(description="Force re-sync slash commands.")
async def sync_commands(interaction: discord.Interaction):
    if not await deny_if_not_owner(interaction): return
    synced = await bot.tree.sync()
    await interaction.response.send_message(f"Synced {len(synced)} command(s).", ephemeral=True)

if __name__ == "__main__":
    if not TOKEN or OWNER_ID == 0:
        raise SystemExit("Please set DISCORD_TOKEN and OWNER_ID environment variables.")
    bot.run(TOKEN)