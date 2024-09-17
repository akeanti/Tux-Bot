import discord
from discord.ext import commands
from discord.ui import Modal, Button, View, Select
import datetime
import json
import os


class TicketConfig:

    def __init__(self):
        self.panel_channel = None
        self.embed_title = "📝 Create a Support Ticket"
        self.embed_description = "Need assistance? Click the button below to create a support ticket."
        self.embed_color = discord.Color.from_rgb(
            249, 158, 147)  # Updated color to #f99e93
        self.embed_image = "https://media.discordapp.net/attachments/1278052479308664884/1284926850799243315/Minimalist_Girl_Gamer_Streaming_Twitch_Banner.png?ex=66e868e2&is=66e71762&hm=54c2eb928befdf1f3ffe80f194fb006e520d22a2b1d2a8bbd13f4378ba486ce5&=&format=webp&quality=lossless&width=1215&height=486"
        self.allowed_roles = []
        self.max_tickets_per_user = 1
        self.max_total_tickets = 50
        self.open_tickets = 0
        self.closed_tickets = 0
        self.ticket_priorities = {}
        self.ticket_resolutions = []
        self.feedback_channel_id = None
        self.admin_role_id = None
        self.load_config()

    def load_config(self):
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                data = json.load(f)
                self.feedback_channel_id = data.get("feedback_channel_id")
                self.admin_role_id = data.get("admin_role_id")

    def save_config(self):
        data = {
            "feedback_channel_id": self.feedback_channel_id,
            "admin_role_id": self.admin_role_id
        }
        with open("config.json", "w") as f:
            json.dump(data, f)


config = TicketConfig()


class TicketModal(Modal):

    def __init__(self, bot):
        super().__init__(title="Ticket Reason")
        self.bot = bot
        self.reason = discord.ui.TextInput(
            label="Reason for opening this ticket",
            style=discord.TextStyle.long,
            required=True)
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        await create_ticket_channel(interaction, self.reason.value, self.bot)


class ClosureReasonModal(Modal):

    def __init__(self, ticket_channel):
        super().__init__(title="Ticket Closure Reason")
        self.ticket_channel = ticket_channel
        self.reason = discord.ui.TextInput(
            label="Reason for closing this ticket",
            style=discord.TextStyle.long,
            required=True)
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        await close_ticket_with_reason(interaction, self.reason.value)


async def create_ticket_channel(interaction: discord.Interaction, reason: str,
                                bot):
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message(
            "This command can only be used in a server.", ephemeral=True)
        return

    user_tickets = [
        ch for ch in guild.text_channels
        if ch.name.startswith(f"ticket-{interaction.user.id}")
    ]
    if len(user_tickets) >= config.max_tickets_per_user:
        await interaction.response.send_message(
            "You already have an open ticket.", ephemeral=True)
        return

    ticket_channels = [
        ch for ch in guild.text_channels if ch.name.startswith("ticket-")
    ]
    if len(ticket_channels) >= config.max_total_tickets:
        await interaction.response.send_message(
            "The server has reached the maximum number of tickets.",
            ephemeral=True)
        return

    category = discord.utils.get(guild.categories, name="Tickets")
    if category is None:
        category = await guild.create_category(name="Tickets")

    overwrites = {
        guild.default_role:
        discord.PermissionOverwrite(read_messages=False),
        interaction.user:
        discord.PermissionOverwrite(read_messages=True, send_messages=True),
    }

    for role in config.allowed_roles:
        overwrites[role] = discord.PermissionOverwrite(read_messages=True,
                                                       send_messages=True)

    ticket_channel = await guild.create_text_channel(
        name=f"ticket-{interaction.user.id}",
        category=category,
        overwrites=overwrites)

    config.open_tickets += 1

    embed = discord.Embed(title=f"Ticket for {interaction.user.name}",
                          description=f"Reason: {reason}",
                          color=config.embed_color)
    embed.set_image(url=config.embed_image)
    embed.set_footer(text="Support Ticket System")

    await ticket_channel.send(
        f"Hello {interaction.user.mention}, a support agent will assist you shortly.",
        embed=embed)

    priority_select = Select(
        placeholder="Select Ticket Priority",
        options=[
            discord.SelectOption(label="Low",
                                 description="Low priority ticket",
                                 value="low"),
            discord.SelectOption(label="Medium",
                                 description="Medium priority ticket",
                                 value="medium"),
            discord.SelectOption(label="High",
                                 description="High priority ticket",
                                 value="high")
        ])

    async def priority_callback(interaction):
        priority = priority_select.values[0]
        config.ticket_priorities[ticket_channel.id] = priority
        await interaction.response.send_message(f"Priority set to {priority}.",
                                                ephemeral=True)

        if priority == "high" and config.admin_role_id:
            admin_role = guild.get_role(config.admin_role_id)
            if admin_role:
                for channel in guild.text_channels:
                    if channel.name == "ticket-logs":
                        await channel.send(embed=discord.Embed(
                            title="High Priority Ticket",
                            description=
                            f"A high priority ticket has been created: {ticket_channel.mention}",
                            color=discord.Color.red()).add_field(
                                name="User", value=interaction.user.mention))
                        break

    priority_select.callback = priority_callback
    priority_view = View()
    priority_view.add_item(priority_select)

    await ticket_channel.send("Set the priority of your ticket:",
                              view=priority_view)

    log_channel = discord.utils.get(guild.text_channels, name="ticket-logs")
    if log_channel is None:
        log_channel = await guild.create_text_channel(name="ticket-logs")

    log_embed = discord.Embed(title="Ticket Created",
                              color=discord.Color.blue())
    log_embed.add_field(name="User",
                        value=interaction.user.mention,
                        inline=True)
    log_embed.add_field(name="Reason", value=reason, inline=False)
    log_embed.add_field(name="Channel",
                        value=ticket_channel.mention,
                        inline=True)
    log_embed.set_footer(text=f"Created at {datetime.datetime.now()}")

    await log_channel.send(embed=log_embed)

    await interaction.response.send_message(
        f"Your ticket has been created: {ticket_channel.mention}",
        ephemeral=True)


async def close_ticket_with_reason(interaction, reason):
    ticket_channel = interaction.channel

    # Ensure that only ticket channels are closed
    if not ticket_channel.name.startswith("ticket-"):
        await interaction.response.send_message(
            "This command can only be used in a ticket channel.",
            ephemeral=True)
        return

    config.closed_tickets += 1

    log_channel = discord.utils.get(interaction.guild.text_channels,
                                    name="ticket-logs")
    if log_channel:
        log_embed = discord.Embed(title="Ticket Closed",
                                  color=discord.Color.red())
        log_embed.add_field(name="User",
                            value=interaction.user.mention,
                            inline=True)
        log_embed.add_field(name="Reason", value=reason, inline=False)
        log_embed.add_field(name="Channel",
                            value=ticket_channel.name,
                            inline=True)
        log_embed.set_footer(text=f"Closed at {datetime.datetime.now()}")
        await log_channel.send(embed=log_embed)

    feedback_channel = interaction.guild.get_channel(
        config.feedback_channel_id)
    if feedback_channel:
        feedback_embed = discord.Embed(
            title="Ticket Closure",
            description=f"Your ticket has been closed. Reason: {reason}",
            color=discord.Color.green())
        await feedback_channel.send(embed=feedback_embed)

    await interaction.user.send(embed=discord.Embed(
        title="Ticket Closure",
        description=f"Your ticket has been closed. Reason: {reason}",
        color=discord.Color.green()))

    # Ensure only the ticket channel is deleted
    await ticket_channel.delete()


class CloseTicketView(View):

    def __init__(self, ticket_channel):
        super().__init__()
        self.ticket_channel = ticket_channel

    @discord.ui.button(label="Confirm Closure",
                       style=discord.ButtonStyle.danger)
    async def confirm_button(self, interaction: discord.Interaction,
                             button: discord.ui.Button):
        await interaction.response.send_modal(
            ClosureReasonModal(self.ticket_channel))

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_button(self, interaction: discord.Interaction,
                            button: discord.ui.Button):
        await interaction.response.send_message("Ticket closure canceled.",
                                                ephemeral=True)

        class FeedbackModal(Modal):

            def __init__(self, bot):
                super().__init__(title="🎤 Ticket Feedback")
                self.bot = bot
                self.feedback = discord.ui.TextInput(
                    label="How was your experience?",
                    style=discord.TextStyle.long,
                    required=True,
                    placeholder="Share your thoughts and suggestions here...",
                )
                self.add_item(self.feedback)

            async def on_submit(self, interaction: discord.Interaction):
                feedback_channel = self.bot.get_channel(
                    config.feedback_channel_id)
                if feedback_channel:
                    embed = discord.Embed(title="New Ticket Feedback",
                                          description=self.feedback.value,
                                          color=discord.Color.gold())
                    embed.set_footer(text=f"Feedback from {interaction.user}",
                                     icon_url=interaction.user.avatar.url)
                    await feedback_channel.send(embed=embed)
                else:
                    await interaction.response.send_message(
                        "Feedback channel not set. Please contact an admin.",
                        ephemeral=True)
                await interaction.response.send_message(
                    "Thank you for your feedback!", ephemeral=True)


class Ticket(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ticket Cog is ready!")

    @discord.app_commands.command(name='ticket',
                                  description='Create a ticket panel.')
    async def ticket(self, interaction: discord.Interaction):
        if not any(
                role.permissions.administrator or role.permissions.manage_roles
                for role in interaction.user.roles):
            await interaction.response.send_message(
                "You do not have permission to use this command.",
                ephemeral=True)
            return

        embed = discord.Embed(title=config.embed_title,
                              description=config.embed_description,
                              color=config.embed_color)
        embed.set_image(url=config.embed_image)
        embed.set_footer(text="Support Ticket Panel")

        button = Button(style=discord.ButtonStyle.primary,
                        label="Create Ticket",
                        custom_id="create_ticket")

        view = View()
        view.add_item(button)

        panel_channel = config.panel_channel or interaction.channel
        await panel_channel.send(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.component:
            if interaction.data['custom_id'] == 'create_ticket':
                await interaction.response.send_modal(TicketModal(self.bot))

    @discord.app_commands.command(name='close',
                                  description='Close an open ticket.')
    async def close_ticket(self, interaction: discord.Interaction):
        ticket_channel = discord.utils.get(
            interaction.guild.text_channels,
            name=f"ticket-{interaction.user.id}")
        if ticket_channel is None:
            await interaction.response.send_message(
                "You do not have an open ticket.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Confirm Ticket Closure",
            description="Are you sure you want to close this ticket?",
            color=discord.Color.orange())

        view = CloseTicketView(ticket_channel)
        await interaction.response.send_message(embed=embed,
                                                view=view,
                                                ephemeral=True)

    @discord.app_commands.command(
        name='ticket-stats',
        description='Display detailed and visually appealing ticket statistics.'
    )
    async def ticket_stats(self, interaction: discord.Interaction):
        try:
            if config.ticket_resolutions:
                avg_resolution = sum(config.ticket_resolutions) / len(
                    config.ticket_resolutions)
            else:
                avg_resolution = 0

            today = datetime.datetime.now().date()

            tickets_opened_today = len([
                ticket for ticket in config.ticket_resolutions
                if ticket.date.date() == today
            ])
            tickets_closed_today = config.closed_tickets - config.open_tickets  # Assume tickets closed today are the difference

            embed = discord.Embed(title="📊 Detailed Ticket Statistics",
                                  color=discord.Color.blurple())
            embed.set_thumbnail(
                url="https://example.com/statistics_thumbnail.png")
            embed.add_field(name="Total Open Tickets",
                            value=f"🔓 {config.open_tickets}",
                            inline=True)
            embed.add_field(name="Total Closed Tickets",
                            value=f"✅ {config.closed_tickets}",
                            inline=True)
            embed.add_field(name="Tickets Opened Today",
                            value=f"📅 {tickets_opened_today}",
                            inline=True)
            embed.add_field(name="Tickets Closed Today",
                            value=f"🗓️ {tickets_closed_today}",
                            inline=True)
            embed.add_field(name="Average Resolution Time",
                            value=f"⏱️ {avg_resolution:.2f} minutes"
                            if avg_resolution > 0 else "N/A",
                            inline=True)

            priority_counts = {
                priority: 0
                for priority in ["low", "medium", "high"]
            }
            for ticket_id in config.ticket_priorities:
                priority = config.ticket_priorities[ticket_id]
                if priority in priority_counts:
                    priority_counts[priority] += 1

            priority_description = "\n".join([
                f"🔹 {p.capitalize()}: {c}" for p, c in priority_counts.items()
            ])
            embed.add_field(name="Ticket Priority Breakdown",
                            value=priority_description,
                            inline=False)

            embed.set_footer(
                text=f"Statistics generated by {self.bot.user.name}",
                icon_url=self.bot.user.avatar.url)

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.response.send_message(
                f"An error occurred while retrieving ticket stats: {e}",
                ephemeral=True)

    @discord.app_commands.command(
        name='feedback', description='Give feedback on a closed ticket.')
    async def feedback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(FeedbackModal(self.bot))

    @discord.app_commands.command(name='set-feedback-channel',
                                  description='Set the feedback channel.')
    @commands.has_role("Admin")
    async def set_feedback_channel(self, interaction: discord.Interaction,
                                   channel: discord.TextChannel):
        config.feedback_channel_id = channel.id
        config.save_config()
        await interaction.response.send_message(
            f"Feedback channel set to {channel.mention}", ephemeral=True)

    @discord.app_commands.command(name='set-admin-role',
                                  description='Set the admin role.')
    @commands.has_role("Admin")
    async def set_admin_role(self, interaction: discord.Interaction,
                             role: discord.Role):
        config.admin_role_id = role.id
        config.save_config()
        await interaction.response.send_message(
            f"Admin role set to {role.name}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Ticket(bot))
