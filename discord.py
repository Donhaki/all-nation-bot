import discord
from discord.ext import commands
from datetime import timedelta

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Bot Online
@bot.event
async def on_ready():
    print(f"{bot.user} is online!")

# =========================
# MODERATION COMMANDS
# =========================

# Kick Command
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.kick(reason=reason)
    await ctx.send(f"✅ {member} was kicked.\nReason: {reason}")

# Ban Command
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member} was banned.\nReason: {reason}")

# Unban Command
@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"✅ {user} was unbanned.")

# Timeout Command
@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, minutes: int, *, reason="No reason provided"):
    duration = timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)
    await ctx.send(f"⏰ {member} timed out for {minutes} minutes.\nReason: {reason}")

# Remove Timeout
@bot.command()
@commands.has_permissions(moderate_members=True)
async def untimeout(ctx, member: discord.Member):
    await member.timeout(None)
    await ctx.send(f"✅ Removed timeout from {member}")

# Warn Command
@bot.command()
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    await ctx.send(f"⚠️ {member} has been warned.\nReason: {reason}")

# Clear Messages
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"🗑️ Deleted {amount} messages.")
    await msg.delete(delay=3)

# Mute Command
@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member):

    role = discord.utils.get(ctx.guild.roles, name="Muted")

    if not role:
        role = await ctx.guild.create_role(name="Muted")

        for channel in ctx.guild.channels:
            await channel.set_permissions(role, send_messages=False, speak=False)

    await member.add_roles(role)
    await ctx.send(f"🔇 {member} has been muted.")

# Unmute Command
@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):

    role = discord.utils.get(ctx.guild.roles, name="Muted")

    await member.remove_roles(role)
    await ctx.send(f"🔊 {member} has been unmuted.")

# Slowmode
@bot.command()
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, seconds: int):
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send(f"🐢 Slowmode set to {seconds} seconds.")

# Lock Channel
@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):

    await ctx.channel.set_permissions(
        ctx.guild.default_role,
        send_messages=False
    )

    await ctx.send("🔒 Channel locked.")

# Unlock Channel
@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):

    await ctx.channel.set_permissions(
        ctx.guild.default_role,
        send_messages=True
    )

    await ctx.send("🔓 Channel unlocked.")

# Ping
@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! {round(bot.latency * 1000)}ms")

# Help Command
@bot.command()
async def helpmod(ctx):

    embed = discord.Embed(
        title="Moderation Commands",
        color=discord.Color.blue()
    )

    embed.add_field(name="!kick @user reason", value="Kick a member", inline=False)
    embed.add_field(name="!ban @user reason", value="Ban a member", inline=False)
    embed.add_field(name="!unban userID", value="Unban a user", inline=False)
    embed.add_field(name="!timeout @user minutes reason", value="Timeout a member", inline=False)
    embed.add_field(name="!untimeout @user", value="Remove timeout", inline=False)
    embed.add_field(name="!warn @user reason", value="Warn a member", inline=False)
    embed.add_field(name="!mute @user", value="Mute a member", inline=False)
    embed.add_field(name="!unmute @user", value="Unmute a member", inline=False)
    embed.add_field(name="!clear amount", value="Delete messages", inline=False)
    embed.add_field(name="!slowmode seconds", value="Set slowmode", inline=False)
    embed.add_field(name="!lock", value="Lock channel", inline=False)
    embed.add_field(name="!unlock", value="Unlock channel", inline=False)
    embed.add_field(name="!ping", value="Bot ping", inline=False)

    await ctx.send(embed=embed)

# Error Handling
@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission.")

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing command arguments.")

    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Member not found.")

    else:
        print(error)

# RUN BOT
bot.run(TOKEN)