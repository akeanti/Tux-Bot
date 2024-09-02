import discord
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Button
import datetime


class TicketConfig:

    def __init__(self):
        self.panel_channel = None
        self.embed_title = "Create a Ticket"
        self.embed_description = "Click the button below to create a support ticket."
        self.embed_color = discord.Color.green()  # Linux-themed green
        self.embed_image = "https://example.com/linux.png"  # Add a relevant Linux-themed image
        self.allowed_roles = []
        self.panel_custom = {
        }  # Dictionary to hold custom panels for different users


config = TicketConfig()


class TicketModal(Modal):

    def __init__(self, bot):
        super().__init__(title="Ticket Reason")
        self.bot = bot
        self.reason = TextInput(label="Reason for opening this ticket",
                                style=discord.TextStyle.long,
                                required=True)
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        await create_ticket_channel(interaction, self.reason.value, self.bot)


async def create_ticket_channel(interaction: discord.Interaction, reason: str,
                                bot):
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message(
            "This command can only be used in a server.", ephemeral=True)
        return

    # Check if the user already has an open ticket
    existing_ticket = discord.utils.get(guild.text_channels,
                                        name=f"ticket-{interaction.user.name}")
    if existing_ticket:
        await interaction.response.send_message(
            "You already have an open ticket.", ephemeral=True)
        return

    # Check if the server has reached the ticket limit
    ticket_channels = [
        ch for ch in guild.text_channels if ch.name.startswith("ticket-")
    ]
    if len(ticket_channels) >= 50:
        await interaction.response.send_message(
            "The server has reached the maximum number of tickets.",
            ephemeral=True)
        return

    # Create ticket channel
    category = discord.utils.get(guild.categories, name="Tickets")
    if category is None:
        category = await guild.create_category(name="Tickets")

    ticket_channel = await guild.create_text_channel(
        name=f"ticket-{interaction.user.name}", category=category)

    # Send a message to the ticket channel
    embed = discord.Embed(title=f"Ticket for {interaction.user.name}",
                          description=f"Reason: {reason}",
                          color=config.embed_color)
    embed.set_image(url=config.embed_image)  # Add an image to the embed
    embed.set_footer(text="Linux Terminal Support")

    await ticket_channel.send(
        f"Hello {interaction.user.mention}, a support agent will assist you shortly.",
        embed=embed)

    # Log the creation of the ticket
    log_channel = discord.utils.get(guild.text_channels, name="ticket-logs")
    if log_channel is None:
        log_channel = await guild.create_text_channel(name="ticket-logs")

    log_message = (
        f"Ticket created by {interaction.user.mention} in {ticket_channel.mention}\n"
        f"Reason: {reason}\n"
        f"Created at: {datetime.datetime.now()}")

    await log_channel.send(log_message)

    # Save log to a text file
    with open("ticket_logs.txt", "a") as file:
        file.write(log_message + "\n")

    await interaction.response.send_message(
        f"Your ticket has been created: {ticket_channel.mention}")


class TicketConfigModal(Modal):

    def __init__(self):
        super().__init__(title="Ticket Panel Configuration")
        self.title = TextInput(label="Panel Title",
                               default=config.embed_title,
                               style=discord.TextStyle.short)
        self.description = TextInput(label="Panel Description",
                                     default=config.embed_description,
                                     style=discord.TextStyle.long)
        self.color = TextInput(label="Embed Color (hex)",
                               default=f"#{config.embed_color.value:06x}",
                               style=discord.TextStyle.short)
        self.image = TextInput(label="Embed Image URL",
                               default=config.embed_image,
                               style=discord.TextStyle.short)
        self.add_item(self.title)
        self.add_item(self.description)
        self.add_item(self.color)
        self.add_item(self.image)

    async def on_submit(self, interaction: discord.Interaction):
        config.embed_title = self.title.value
        config.embed_description = self.description.value
        try:
            config.embed_color = discord.Color(
                int(self.color.value.strip("#"), 16))
        except ValueError:
            await interaction.response.send_message(
                "Invalid color code. Using default color.", ephemeral=True)
            config.embed_color = discord.Color.green()
        config.embed_image = self.image.value

        await interaction.response.send_message(
            "Ticket panel configuration updated.")


class Ticket(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ticket Cog is ready!")

    @discord.app_commands.command(name='ticket',
                                  description='Create a ticket panel.')
    async def ticket(self, interaction: discord.Interaction):
        """Creates a ticket panel."""
        # Check if the user has admin or moderator permissions
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
        """Closes an open ticket."""
        ticket_channel = discord.utils.get(
            interaction.guild.text_channels,
            name=f"ticket-{interaction.user.name}")
        if ticket_channel is None:
            await interaction.response.send_message(
                "You do not have an open ticket.")
            return

        # Log the closure
        log_channel = discord.utils.get(interaction.guild.text_channels,
                                        name="ticket-logs")
        if log_channel is None:
            log_channel = await interaction.guild.create_text_channel(
                name="ticket-logs")

        log_message = (
            f"Ticket closed by {interaction.user.mention} in {ticket_channel.mention}\n"
            f"Closed at: {datetime.datetime.now()}")

        await log_channel.send(log_message)

        # Save log to a text file
        with open("ticket_logs.txt", "a") as file:
            file.write(log_message + "\n")

        await ticket_channel.send("This ticket is now closed.")
        await ticket_channel.delete()

        await interaction.response.send_message("The ticket has been closed.")

    @discord.app_commands.command(name='setpanel',
                                  description='Set the ticket panel channel.')
    @commands.has_permissions(
        administrator=True)  # Ensure only admins can use this
    async def set_panel(self, interaction: discord.Interaction):
        """Set the channel where the ticket panel will be sent."""
        config.panel_channel = interaction.channel
        await interaction.response.send_message(
            f"Ticket panel channel set to {interaction.channel.mention}.")

    @discord.app_commands.command(
        name='setroles', description='Set the roles that can access tickets.')
    @commands.has_permissions(
        administrator=True)  # Ensure only admins can use this
    async def set_roles(self, interaction: discord.Interaction,
                        roles: discord.Role):
        """Set the roles allowed to access tickets."""
        config.allowed_roles.append(roles)
        role_mentions = ', '.join(
            [role.mention for role in config.allowed_roles])
        await interaction.response.send_message(
            f"Roles allowed to access tickets: {role_mentions}.")

    @discord.app_commands.command(
        name='ticket-help', description='Display all ticket-related commands.')
    async def ticket_help(self, interaction: discord.Interaction):
        """Displays a help message with all available ticket commands."""
        commands_list = [
            "/ticket - Create a ticket panel", "/close - Close an open ticket",
            "/setpanel - Set the ticket panel channel",
            "/setroles - Set the roles that can access tickets",
            "/configticket - Configure the ticket panel",
            "/ticket-help - Display this help message",
            "/ls-tickets - List all open tickets",
            "/rm-ticket - Remove a specific ticket by name"
        ]
        embed = discord.Embed(title="Ticket Bot Help",
                              description="\n".join(commands_list),
                              color=discord.Color.green())
        await interaction.channel.send(embed=embed)

    @discord.app_commands.command(name='ls-tickets',
                                  description='List all open tickets.')
    async def ls_tickets(self, interaction: discord.Interaction):
        """Lists all open tickets in the server."""
        ticket_channels = [
            ch for ch in interaction.guild.text_channels
            if ch.name.startswith("ticket-")
        ]
        if not ticket_channels:
            await interaction.response.send_message(
                "There are no open tickets.")
            return

        ticket_list = "\n".join(
            [f"{ch.name}: {ch.mention}" for ch in ticket_channels])
        await interaction.response.send_message(f"Open tickets:\n{ticket_list}"
                                                )

    @discord.app_commands.command(
        name='rm-ticket', description='Remove a specific ticket by name.')
    async def rm_ticket(self, interaction: discord.Interaction,
                        ticket_name: str):
        """Removes a specific ticket by name."""
        ticket_channel = discord.utils.get(interaction.guild.text_channels,
                                           name=ticket_name)
        if ticket_channel is None:
            await interaction.response.send_message(
                "No ticket found with that name.")
            return

        await ticket_channel.delete()
        await interaction.response.send_message(
            f"Ticket '{ticket_name}' has been removed.")


async def setup(bot):
    await bot.add_cog(Ticket(bot))
