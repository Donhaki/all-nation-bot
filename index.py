import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} is online!")

# Send a normal message
@bot.command()
async def say(ctx, *, message):
    await ctx.send(message)

# Send an embed
@bot.command()
async def embed(ctx):
    embed = discord.Embed(
        title="Welcome",
        description="This is a test embed.",
        color=discord.Color.green()
    )

    embed.set_footer(text="My Discord Bot")

    await ctx.send(embed=embed)

# Send a DM
@bot.command()
async def dm(ctx, member: discord.Member, *, message):
    await member.send(message)
    await ctx.send("DM sent!")

# Send custom message to any channel
@bot.command()
async def sendto(ctx, channel: discord.TextChannel, *, message):
    await channel.send(message)
    await ctx.send("Message sent!")

# Send custom embed

@bot.command()
async def customembed(ctx, title, *, description):
    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.blue()
    )

    await ctx.send(embed=embed)

bot.run(TOKEN)