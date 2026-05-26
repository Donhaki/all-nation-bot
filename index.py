# ticket_bot.py
# Ticket Bot With:
# - Ticket Panel
# - Logging System
# - Rating Inside Same Ticket
# - Auto Delete After Rating
# - No Claim System

import discord
from discord.ext import commands
import json
import os
from datetime import datetime

# =========================================
# CONFIG
# =========================================

TOKEN = "YOUR_BOT_TOKEN"

GUILD_ID = YOUR_GUILD_ID
STAFF_ROLE_ID = YOUR_STAFF_ROLE_ID
CATEGORY_ID = YOUR_CATEGORY_ID

LOG_CHANNEL_ID = YOUR_LOG_CHANNEL_ID
RATING_LOG_CHANNEL_ID = YOUR_RATING_LOG_CHANNEL_ID

# =========================================
# BOT SETUP
# =========================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# =========================================
# DATABASE
# =========================================

if not os.path.exists("tickets.json"):
    with open("tickets.json", "w") as f:
        json.dump({}, f)

def load_data():
    with open("tickets.json", "r") as f:
        return json.load(f)

def save_data(data):
    with open("tickets.json", "w") as f:
        json.dump(data, f, indent=4)

# =========================================
# RATING SYSTEM
# =========================================

class RatingView(discord.ui.View):

    def __init__(self, ticket_owner_id):
        super().__init__(timeout=300)
        self.ticket_owner_id = ticket_owner_id

    async def submit_rating(
        self,
        interaction: discord.Interaction,
        stars: int
    ):

        # ONLY TICKET OWNER CAN RATE
        if interaction.user.id != self.ticket_owner_id:
            await interaction.response.send_message(
                "Only the ticket creator can rate.",
                ephemeral=True
            )
            return

        rating_channel = interaction.guild.get_channel(
            RATING_LOG_CHANNEL_ID
        )

        # LOG RATING
        embed = discord.Embed(
            title="New Support Rating",
            color=discord.Color.gold(),
            timestamp=datetime.utcnow()
        )

        embed.add_field(
            name="User",
            value=interaction.user.mention,
            inline=False
        )

        embed.add_field(
            name="Rating",
            value=f"{'⭐' * stars} ({stars}/5)",
            inline=False
        )

        embed.add_field(
            name="Ticket",
            value=interaction.channel.name,
            inline=False
        )

        await rating_channel.send(embed=embed)

        await interaction.response.edit_message(
            content=(
                f"✅ Thanks for rating the support "
                f"{'⭐' * stars}\n\n"
                "This ticket will delete in 5 seconds."
            ),
            embed=None,
            view=None
        )

        await interaction.channel.delete(delay=5)

    @discord.ui.button(label="⭐", style=discord.ButtonStyle.gray)
    async def one(self, interaction, button):
        await self.submit_rating(interaction, 1)

    @discord.ui.button(label="⭐⭐", style=discord.ButtonStyle.gray)
    async def two(self, interaction, button):
        await self.submit_rating(interaction, 2)

    @discord.ui.button(label="⭐⭐⭐", style=discord.ButtonStyle.blurple)
    async def three(self, interaction, button):
        await self.submit_rating(interaction, 3)

    @discord.ui.button(label="⭐⭐⭐⭐", style=discord.ButtonStyle.green)
    async def four(self, interaction, button):
        await self.submit_rating(interaction, 4)

    @discord.ui.button(label="⭐⭐⭐⭐⭐", style=discord.ButtonStyle.green)
    async def five(self, interaction, button):
        await self.submit_rating(interaction, 5)

# =========================================
# CLOSE BUTTON
# =========================================

class CloseTicketView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Close Ticket",
        style=discord.ButtonStyle.red,
        emoji="🔒",
        custom_id="close_ticket"
    )
    async def close_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        staff_role = interaction.guild.get_role(STAFF_ROLE_ID)

        # STAFF ONLY
        if staff_role not in interaction.user.roles:
            await interaction.response.send_message(
                "You are not allowed to close tickets.",
                ephemeral=True
            )
            return

        data = load_data()

        ticket_data = data.get(str(interaction.channel.id))

        if not ticket_data:
            await interaction.response.send_message(
                "Ticket data not found.",
                ephemeral=True
            )
            return

        owner = interaction.guild.get_member(
            ticket_data["owner_id"]
        )

        # LOG TICKET
        log_channel = interaction.guild.get_channel(
            LOG_CHANNEL_ID
        )

        log_embed = discord.Embed(
            title="Ticket Closed",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )

        log_embed.add_field(
            name="Ticket",
            value=interaction.channel.name,
            inline=False
        )

        log_embed.add_field(
            name="Closed By",
            value=interaction.user.mention,
            inline=False
        )

        log_embed.add_field(
            name="Ticket Owner",
            value=owner.mention,
            inline=False
        )

        await log_channel.send(embed=log_embed)

        # SEND RATING PANEL IN SAME CHANNEL
        rating_embed = discord.Embed(
            title="Rate Your Support Experience",
            description=(
                f"{owner.mention}, please rate the support "
                "you received before the ticket closes."
            ),
            color=discord.Color.orange()
        )

        await interaction.response.send_message(
            embed=rating_embed,
            view=RatingView(owner.id)
        )

# =========================================
# CREATE TICKET BUTTON
# =========================================

class TicketPanel(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Create Ticket",
        style=discord.ButtonStyle.green,
        emoji="🎫",
        custom_id="create_ticket"
    )
    async def create_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        guild = interaction.guild

        # CHECK EXISTING TICKET
        existing = discord.utils.get(
            guild.text_channels,
            name=f"ticket-{interaction.user.name.lower()}"
        )

        if existing:
            await interaction.response.send_message(
                f"You already have a ticket: {existing.mention}",
                ephemeral=True
            )
            return

        category = guild.get_channel(CATEGORY_ID)
        staff_role = guild.get_role(STAFF_ROLE_ID)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                read_messages=False
            ),

            interaction.user: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                attach_files=True
            ),

            staff_role: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True
            )
        }

        # CREATE CHANNEL
        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        # SAVE TICKET
        data = load_data()

        data[str(channel.id)] = {
            "owner_id": interaction.user.id,
            "created_at": str(datetime.utcnow())
        }

        save_data(data)

        embed = discord.Embed(
            title="Support Ticket",
            description=(
                f"{interaction.user.mention}, "
                "please explain your issue.\n\n"
                "A staff member will assist you shortly."
            ),
            color=discord.Color.blurple()
        )

        embed.set_footer(
            text="Press the button below when finished."
        )

        await channel.send(
            content=f"{interaction.user.mention} {staff_role.mention}",
            embed=embed,
            view=CloseTicketView()
        )

        await interaction.response.send_message(
            f"✅ Ticket created: {channel.mention}",
            ephemeral=True
        )

# =========================================
# PANEL COMMAND
# =========================================

@bot.command()
@commands.has_permissions(administrator=True)
async def panel(ctx):

    embed = discord.Embed(
        title="Support Tickets",
        description=(
            "Need help?\n\n"
            "Press the button below to create a ticket."
        ),
        color=discord.Color.green()
    )

    await ctx.send(
        embed=embed,
        view=TicketPanel()
    )

# =========================================
# READY EVENT
# =========================================

@bot.event
async def on_ready():

    bot.add_view(TicketPanel())
    bot.add_view(CloseTicketView())

    print(f"Logged in as {bot.user}")

# =========================================
# START BOT
# =========================================

bot.run(TOKEN)