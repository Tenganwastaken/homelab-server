"""
Discord Bot — Full Featured Server Bot
Features:
  - Reaction roles (game roles via emoji reactions)
  - Join-to-create private voice rooms
  - Welcome embed + DM on member join
  - React-to-verify gate
  - !server-update announcement command
"""

import discord
from discord.ext import commands
import json
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────
# CONFIGURATION (set in .env)
# ─────────────────────────────────────────
TOKEN                     = os.getenv("DISCORD_TOKEN")
GUILD_ID                  = int(os.getenv("GUILD_ID", "0"))
WELCOME_CHANNEL_ID        = int(os.getenv("WELCOME_CHANNEL_ID", "0"))
VERIFY_CHANNEL_ID         = int(os.getenv("VERIFY_CHANNEL_ID", "0"))
VERIFY_MESSAGE_ID         = int(os.getenv("VERIFY_MESSAGE_ID", "0"))
VERIFIED_ROLE_ID          = int(os.getenv("VERIFIED_ROLE_ID", "0"))
REACTION_ROLES_MESSAGE_ID = int(os.getenv("REACTION_ROLES_MESSAGE_ID", "0"))
VOICE_CREATOR_CHANNEL_ID  = int(os.getenv("VOICE_CREATOR_CHANNEL_ID", "0"))
UPDATES_CHANNEL_ID        = int(os.getenv("UPDATES_CHANNEL_ID", "0"))

# Emoji → Role ID mapping for game roles
# Add one entry per game role in your server
GAME_ROLES: dict[str, int] = {
    "🎮": int(os.getenv("GAME1_ROLE_ID", "0")),   # e.g. Valorant
    "⚔️": int(os.getenv("GAME2_ROLE_ID", "0")),    # e.g. League of Legends
    "🎯": int(os.getenv("GAME3_ROLE_ID", "0")),    # e.g. CS2
    "🏎️": int(os.getenv("GAME4_ROLE_ID", "0")),    # e.g. Rocket League
    "🌍": int(os.getenv("GAME5_ROLE_ID", "0")),    # e.g. GTA
    "⚡": int(os.getenv("GAME6_ROLE_ID", "0")),    # e.g. Fortnite
    "🎲": int(os.getenv("GAME7_ROLE_ID", "0")),    # e.g. Minecraft
    "🔫": int(os.getenv("GAME8_ROLE_ID", "0")),    # e.g. Warzone
    "🐉": int(os.getenv("GAME9_ROLE_ID", "0")),    # e.g. World of Warcraft
}

# ─────────────────────────────────────────
# PERSISTENT STORAGE HELPERS
# ─────────────────────────────────────────
VOICE_CREATOR_FILE = "voice_creator.json"   # {channel_id: owner_user_id}


def load_json(filename: str) -> dict:
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_json(filename: str, data: dict) -> None:
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


# ─────────────────────────────────────────
# BOT SETUP
# ─────────────────────────────────────────
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


# ─────────────────────────────────────────
# READY EVENT
# ─────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="the server"
        )
    )


# ─────────────────────────────────────────
# WELCOME — Member Join
# Sends an embed in the welcome channel
# and a DM with server info
# ─────────────────────────────────────────
@bot.event
async def on_member_join(member: discord.Member):
    guild = member.guild

    # Welcome channel embed
    channel = guild.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title=f"Welcome to {guild.name}! 👋",
            description=(
                f"Hey {member.mention}, glad you're here!\n\n"
                f"**To get started:**\n"
                f"1. Head to the verify channel and react to get access\n"
                f"2. Pick your game roles in the roles channel\n"
                f"3. Introduce yourself!\n\n"
                f"Enjoy your stay 🎉"
            ),
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Member #{guild.member_count}")
        await channel.send(embed=embed)

    # DM the new member
    try:
        dm_embed = discord.Embed(
            title=f"Welcome to {guild.name}!",
            description=(
                f"Thanks for joining! Here's what to do:\n\n"
                f"• **Verify** yourself in the verification channel\n"
                f"• **Pick game roles** to see game-specific channels\n"
                f"• **Create a voice room** by joining the 'Create VC' channel\n\n"
                f"Have fun! 🎮"
            ),
            color=discord.Color.green()
        )
        await member.send(embed=dm_embed)
    except discord.Forbidden:
        pass  # User has DMs disabled


# ─────────────────────────────────────────
# VERIFY GATE — React to get the verified role
# Set up: post a message in your verify channel,
# copy its ID to VERIFY_MESSAGE_ID in .env
# ─────────────────────────────────────────
@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.user_id == bot.user.id:
        return

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return

    member = guild.get_member(payload.user_id)
    if not member:
        return

    # ── Verify gate ──────────────────────
    if (
        payload.message_id == VERIFY_MESSAGE_ID
        and str(payload.emoji) == "✅"
    ):
        role = guild.get_role(VERIFIED_ROLE_ID)
        if role and role not in member.roles:
            await member.add_roles(role, reason="Verified via reaction")
            print(f"✅ Verified: {member}")

    # ── Game reaction roles ───────────────
    if (
        payload.message_id == REACTION_ROLES_MESSAGE_ID
        and str(payload.emoji) in GAME_ROLES
    ):
        role_id = GAME_ROLES[str(payload.emoji)]
        role = guild.get_role(role_id)
        if role and role not in member.roles:
            await member.add_roles(role, reason="Reaction role")
            print(f"🎮 Added role {role.name} → {member}")


@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    if payload.user_id == bot.user.id:
        return

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return

    member = guild.get_member(payload.user_id)
    if not member:
        return

    # ── Remove game role on un-react ─────
    if (
        payload.message_id == REACTION_ROLES_MESSAGE_ID
        and str(payload.emoji) in GAME_ROLES
    ):
        role_id = GAME_ROLES[str(payload.emoji)]
        role = guild.get_role(role_id)
        if role and role in member.roles:
            await member.remove_roles(role, reason="Reaction role removed")
            print(f"🎮 Removed role {role.name} ← {member}")


# ─────────────────────────────────────────
# JOIN-TO-CREATE VOICE ROOMS
# When a user joins the designated VC creator
# channel, a private channel is created for them.
# The channel is deleted when everyone leaves.
# ─────────────────────────────────────────
@bot.event
async def on_voice_state_update(
    member: discord.Member,
    before: discord.VoiceState,
    after: discord.VoiceState
):
    voice_data = load_json(VOICE_CREATOR_FILE)

    # ── User joined the creator channel ──
    if after.channel and after.channel.id == VOICE_CREATOR_CHANNEL_ID:
        guild = member.guild
        category = after.channel.category

        # Create a private channel only visible to that member (and admins)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(connect=False),
            member: discord.PermissionOverwrite(
                connect=True,
                manage_channels=True,
                move_members=True
            )
        }

        new_channel = await guild.create_voice_channel(
            name=f"🔒 {member.display_name}'s Room",
            category=category,
            overwrites=overwrites
        )
        await member.move_to(new_channel)

        # Track the channel
        voice_data[str(new_channel.id)] = member.id
        save_json(VOICE_CREATOR_FILE, voice_data)
        print(f"🔊 Created voice room for {member}: {new_channel.name}")

    # ── User left a tracked channel ──────
    if before.channel and str(before.channel.id) in voice_data:
        channel = before.channel
        # Delete if empty
        if len(channel.members) == 0:
            channel_id = str(channel.id)
            await channel.delete(reason="Empty join-to-create room")
            voice_data.pop(channel_id, None)
            save_json(VOICE_CREATOR_FILE, voice_data)
            print(f"🗑️  Deleted empty voice room: {channel.name}")


# ─────────────────────────────────────────
# !server-update — Post a formatted update
# Usage: !server-update <message>
# Restricted to members with Manage Server perm
# ─────────────────────────────────────────
@bot.command(name="server-update")
@commands.has_permissions(manage_guild=True)
async def server_update(ctx: commands.Context, *, message: str):
    channel = ctx.guild.get_channel(UPDATES_CHANNEL_ID)
    if not channel:
        await ctx.send("❌ Updates channel not found. Check UPDATES_CHANNEL_ID in config.", delete_after=10)
        return

    embed = discord.Embed(
        title="📢 Server Update",
        description=message,
        color=discord.Color.gold()
    )
    embed.set_footer(text=f"Posted by {ctx.author.display_name}")
    embed.timestamp = discord.utils.utcnow()

    await channel.send(embed=embed)
    await ctx.message.delete()
    print(f"📢 Server update posted by {ctx.author}")


@server_update.error
async def server_update_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need **Manage Server** permission to use this command.", delete_after=10)


# ─────────────────────────────────────────
# RUN
# ─────────────────────────────────────────
if __name__ == "__main__":
    bot.run(TOKEN)
