import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def send_mod_message(self, member, action, reason=None):
        """Send a direct message to the member who performed an action."""
        try:
            dm_message = f"Your action of `{action}` has been executed."
            if reason:
                dm_message += f"\nReason: {reason}"
            await member.send(dm_message)
        except discord.Forbidden:
            pass  # Handle if the bot cannot send DMs

    @app_commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        """Ban a member from the server."""
        await member.ban(reason=reason)

        embed = discord.Embed(
            title="🚫 Ban Command",
            description=f"{member} has been banned from the server.",
            color=discord.Color.red()
        )
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)

        await interaction.response.send_message(embed=embed)
        await self.send_mod_message(interaction.user, "ban", reason)

    @app_commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        """Kick a member from the server."""
        await member.kick(reason=reason)

        embed = discord.Embed(
            title="🔨 Kick Command",
            description=f"{member} has been kicked from the server.",
            color=discord.Color.orange()
        )
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)

        await interaction.response.send_message(embed=embed)
        await self.send_mod_message(interaction.user, "kick", reason)

    @app_commands.command(name="mute")
    @commands.has_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member, duration: int):
        """Mute a member for a specified duration."""
        mute_role = discord.utils.get(member.guild.roles, name="Muted")
        if mute_role:
            await member.add_roles(mute_role)
            embed = discord.Embed(
                title="🔇 Mute Command",
                description=f"{member} has been muted for {duration} minutes.",
                color=discord.Color.purple()
            )
            embed.add_field(name="Duration", value=f"{duration} minutes", inline=False)
            await interaction.response.send_message(embed=embed)
            await self.send_mod_message(interaction.user, "mute", f"{duration} minutes")
        else:
            await interaction.response.send_message("Mute role not found.")

    @app_commands.command(name="warn")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, *, reason: str):
        """Warn a member and send them a DM."""
        embed = discord.Embed(
            title="⚠️ Warning",
            description=f"You have been warned by {interaction.user}.",
            color=discord.Color.yellow()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        await member.send(embed=embed)

        embed = discord.Embed(
            title="⚠️ Warn Command",
            description=f"{member} has been warned.",
            color=discord.Color.yellow()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="addrole")
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        """Add a role to a member."""
        if role in interaction.guild.roles:
            await member.add_roles(role)
            embed = discord.Embed(
                title="🎖️ Add Role",
                description=f"{role} role has been added to {member}.",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Role not found.")

    @app_commands.command(name="removerole")
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        """Remove a role from a member."""
        if role in interaction.guild.roles:
            await member.remove_roles(role)
            embed = discord.Embed(
                title="❌ Remove Role",
                description=f"{role} role has been removed from {member}.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Role not found.")

    @app_commands.command(name="tempmute")
    @commands.has_permissions(moderate_members=True)
    async def tempmute(self, interaction: discord.Interaction, member: discord.Member, duration: int):
        """Temporarily mute a member for a specified duration."""
        mute_role = discord.utils.get(member.guild.roles, name="Muted")
        if mute_role:
            await member.add_roles(mute_role)
            embed = discord.Embed(
                title="🔇 Temporary Mute",
                description=f"{member} has been muted for {duration} minutes.",
                color=discord.Color.purple()
            )
            embed.add_field(name="Duration", value=f"{duration} minutes", inline=False)
            await interaction.response.send_message(embed=embed)
            await self.send_mod_message(interaction.user, "tempmute", f"{duration} minutes")
            await asyncio.sleep(duration * 60)
            await member.remove_roles(mute_role)
            await interaction.channel.send(f"{member} has been unmuted after {duration} minutes.")
        else:
            await interaction.response.send_message("Mute role not found.")

    @app_commands.command(name="timeout")
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, duration: int):
        """Temporarily puts a user in timeout for a specified duration."""
        timeout_role = discord.utils.get(member.guild.roles, name="Timeout")
        if timeout_role:
            await member.add_roles(timeout_role)
            embed = discord.Embed(
                title="⏳ Timeout",
                description=f"{member} has been put in timeout for {duration} minutes.",
                color=discord.Color.orange()
            )
            embed.add_field(name="Duration", value=f"{duration} minutes", inline=False)
            await interaction.response.send_message(embed=embed)
            await self.send_mod_message(interaction.user, "timeout", f"{duration} minutes")
            await asyncio.sleep(duration * 60)
            await member.remove_roles(timeout_role)
            await interaction.channel.send(f"{member} has been removed from timeout after {duration} minutes.")
        else:
            await interaction.response.send_message("Timeout role not found.")

    @app_commands.command(name="lock")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Lock a channel to prevent sending messages."""
        await channel.set_permissions(interaction.guild.default_role, send_messages=False)
        embed = discord.Embed(
            title="🔒 Lock Channel",
            description=f"{channel.mention} has been locked.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="unlock")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Unlock a channel to allow sending messages."""
        await channel.set_permissions(interaction.guild.default_role, send_messages=True)
        embed = discord.Embed(
            title="🔓 Unlock Channel",
            description=f"{channel.mention} has been unlocked.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="createmute")
    @commands.has_permissions(manage_roles=True)
    async def createmute(self, interaction: discord.Interaction):
        """Create a 'Muted' role if it doesn't already exist."""
        guild = interaction.guild
        existing_role = discord.utils.get(guild.roles, name="Muted")

        if existing_role:
            await interaction.response.send_message("The 'Muted' role already exists.")
            return

        try:
            mute_role = await guild.create_role(name="Muted", color=discord.Color.greyple(), permissions=discord.Permissions(send_messages=False))
            for channel in guild.channels:
                await channel.set_permissions(mute_role, send_messages=False)
            embed = discord.Embed(
                title="✅ Role Created",
                description="The 'Muted' role has been created and applied to all channels.",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to create roles.")
        except discord.HTTPException as e:
            await interaction.response.send_message(f"An error occurred: {e}")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
