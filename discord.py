import discord
import datetime
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
from dotenv import load_dotenv
import json
import os
import re

load_dotenv()

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# KICK COMMAND
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"{member} was kicked.")

# BAN COMMAND
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"{member} was banned.")

# KICK COMMAND
@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, minutes: int, *, reason=None):
    duration = timedelta(minutes=minutes)
    
    await member.timeout(duration, reason=reason)
    await ctx.send(
    f"{member.mention} has been timed out for {minutes} minute(s).\nReason: {reason}"
    )
    
# CLEAR MESSAGES
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount)
    await ctx.send(f"Deleted {amount} messages.", delete_after=3)

bot.run (TOKEN)