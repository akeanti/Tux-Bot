import discord
from discord.ext import commands
from discord import app_commands
import aiohttp


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.webhook_url = None  # Store the webhook URL

    async def send_webhook_log(self, embed: discord.Embed):
        """Send a log message to the webhook."""
        if self.webhook_url:
            async with aiohttp.ClientSession() as session:
                webhook = discord.Webhook.from_url(self.webhook_url,
                                                   session=session)
                await webhook.send(embed=embed)
        else:
            print("Webhook URL not set")

    @app_commands.command(name="setwebhook")
    @commands.has_permissions(administrator=True)
    async def setwebhook(self, interaction: discord.Interaction, url: str):
        """Set the webhook URL for logging moderation actions."""
        self.webhook_url = url
        await interaction.response.send_message(f"Webhook URL set to {url}")

    async def send_mod_message(self, member, action, reason=None):
        """Send a direct message to the member who performed an action."""
        try:
            dm_message = f"Your action of {action} has been executed."
            if reason:
                dm_message += f"\nReason: {reason}"
            await member.send(dm_message)
        except discord.Forbidden:
            pass  # Handle if the bot cannot send DMs

    @app_commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self,
                  interaction: discord.Interaction,
                  member: discord.Member,
                  reason: str = None):
        """Ban a member from the server."""
        # Check if the user has admin or moderator permissions
        if not any(
                role.permissions.administrator or role.permissions.manage_roles
                for role in interaction.user.roles):
            await interaction.response.send_message(
                "You do not have permission to use this command.",
                ephemeral=True)
            return
        await member.ban(reason=reason)

        embed = discord.Embed(
            title="🚫 Ban Command",
            description=f"{member} has been banned from the server.",
            color=discord.Color.red())
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)

        await interaction.response.send_message(embed=embed)
        await self.send_mod_message(interaction.user, "ban", reason)
        await self.send_webhook_log(embed)

    @app_commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self,
                   interaction: discord.Interaction,
                   member: discord.Member,
                   reason: str = None):
        """Kick a member from the server."""
        # Check if the user has admin or moderator permissions
        if not any(
                role.permissions.administrator or role.permissions.manage_roles
                for role in interaction.user.roles):
            await interaction.response.send_message(
                "You do not have permission to use this command.",
                ephemeral=True)
            return
        await member.kick(reason=reason)

        embed = discord.Embed(
            title="🔨 Kick Command",
            description=f"{member} has been kicked from the server.",
            color=discord.Color.orange())
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)

        await interaction.response.send_message(embed=embed)
        await self.send_mod_message(interaction.user, "kick", reason)
        await self.send_webhook_log(embed)

    @app_commands.command(name="mute")
    @commands.has_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction,
                   member: discord.Member, duration: int):
        """Mute a member for a specified duration."""
        # Check if the user has admin or moderator permissions
        if not any(
                role.permissions.administrator or role.permissions.manage_roles
                for role in interaction.user.roles):
            await interaction.response.send_message(
                "You do not have permission to use this command.",
                ephemeral=True)
            return
        mute_role = discord.utils.get(member.guild.roles, name="Muted")
        if mute_role:
            await member.add_roles(mute_role)
            embed = discord.Embed(
                title="🔇 Mute Command",
                description=f"{member} has been muted for {duration} minutes.",
                color=discord.Color.purple())
            embed.add_field(name="Duration",
                            value=f"{duration} minutes",
                            inline=False)
            await interaction.response.send_message(embed=embed)
            await self.send_mod_message(interaction.user, "mute",
                                        f"{duration} minutes")
            await self.send_webhook_log(embed)
        else:
            await interaction.response.send_message("Mute role not found.")

    @app_commands.command(name="warn")
    async def warn(self, interaction: discord.Interaction,
                   member: discord.Member, *, reason: str):
        """Warn a member and send them a DM."""
        # Check if the user has admin or moderator permissions
        if not any(
                role.permissions.administrator or role.permissions.manage_roles
                for role in interaction.user.roles):
            await interaction.response.send_message(
                "You do not have permission to use this command.",
                ephemeral=True)
            return
        embed = discord.Embed(
            title="⚠️ Warning",
            description=f"You have been warned by {interaction.user}.",
            color=discord.Color.yellow())
        embed.add_field(name="Reason", value=reason, inline=False)
        await member.send(embed=embed)

        embed = discord.Embed(title="⚠️ Warn Command",
                              description=f"{member} has been warned.",
                              color=discord.Color.yellow())
        embed.add_field(name="Reason", value=reason, inline=False)
        await interaction.response.send_message(embed=embed)
        await self.send_webhook_log(embed)

    @app_commands.command(name="lock")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, interaction: discord.Interaction,
                   channel: discord.TextChannel):
        """Lock a channel to prevent sending messages."""
        # Check if the user has admin or moderator permissions
        if not any(
                role.permissions.administrator or role.permissions.manage_roles
                for role in interaction.user.roles):
            await interaction.response.send_message(
                "You do not have permission to use this command.",
                ephemeral=True)
            return
        await channel.set_permissions(interaction.guild.default_role,
                                      send_messages=False)
        embed = discord.Embed(
            title="🔒 Lock Channel",
            description=f"{channel.mention} has been locked.",
            color=discord.Color.red())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="unlock")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, interaction: discord.Interaction,
                     channel: discord.TextChannel):
        """Unlock a channel to allow sending messages."""
        # Check if the user has admin or moderator permissions
        if not any(
                role.permissions.administrator or role.permissions.manage_roles
                for role in interaction.user.roles):
            await interaction.response.send_message(
                "You do not have permission to use this command.",
                ephemeral=True)
            return
        await channel.set_permissions(interaction.guild.default_role,
                                      send_messages=True)
        embed = discord.Embed(
            title="🔓 Unlock Channel",
            description=f"{channel.mention} has been unlocked.",
            color=discord.Color.green())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="createmute")
    @commands.has_permissions(manage_roles=True)
    async def createmute(self, interaction: discord.Interaction):
        """Create a 'Muted' role if it doesn't already exist."""
        # Check if the user has admin or moderator permissions
        if not any(
                role.permissions.administrator or role.permissions.manage_roles
                for role in interaction.user.roles):
            await interaction.response.send_message(
                "You do not have permission to use this command.",
                ephemeral=True)
            return
        guild = interaction.guild
        existing_role = discord.utils.get(guild.roles, name="Muted")

        if existing_role:
            await interaction.response.send_message(
                "The 'Muted' role already exists.")
            return

        try:
            mute_role = await guild.create_role(
                name="Muted",
                color=discord.Color.greyple(),
                permissions=discord.Permissions(send_messages=False))
            for channel in guild.channels:
                await channel.set_permissions(mute_role, send_messages=False)
            embed = discord.Embed(
                title="✅ Role Created",
                description=
                "The 'Muted' role has been created and applied to all channels.",
                color=discord.Color.green())
            await interaction.response.send_message(embed=embed)
        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permission to create roles.")
        except discord.HTTPException as e:
            await interaction.response.send_message(f"An error occurred: {e}")

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        """Log when a member is banned."""
        embed = discord.Embed(
            title="🚫 Member Banned",
            description=f"{user} has been banned from the server.",
            color=discord.Color.red())
        await self.send_webhook_log(embed)

    @commands.Cog.listener()
    async def on_member_kick(self, member: discord.Member):
        """Log when a member is kicked."""
        embed = discord.Embed(
            title="🔨 Member Kicked",
            description=f"{member} has been kicked from the server.",
            color=discord.Color.orange())
        await self.send_webhook_log(embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """Log when a message is deleted."""
        embed = discord.Embed(
            title="🗑️ Message Deleted",
            description=f"Message from {message.author} has been deleted.",
            color=discord.Color.orange())
        embed.add_field(name="Content", value=message.content, inline=False)
        await self.send_webhook_log(embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message,
                              after: discord.Message):
        """Log when a message is edited."""
        if before.content != after.content:
            embed = discord.Embed(
                title="✏️ Message Edited",
                description=f"Message from {before.author} has been edited.",
                color=discord.Color.gold())
            embed.add_field(name="Before", value=before.content, inline=False)
            embed.add_field(name="After", value=after.content, inline=False)
            await self.send_webhook_log(embed)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member,
                               after: discord.Member):
        """Log when a member's profile is updated."""
        if before.nick != after.nick:
            embed = discord.Embed(
                title="✏️ Nickname Changed",
                description=f"{before} changed their nickname.",
                color=discord.Color.blue())
            embed.add_field(name="Before",
                            value=before.nick or "None",
                            inline=False)
            embed.add_field(name="After",
                            value=after.nick or "None",
                            inline=False)
            await self.send_webhook_log(embed)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
