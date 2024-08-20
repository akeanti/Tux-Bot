import discord
from discord.ext import commands
from discord import app_commands


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
    async def ban(self,
                  interaction: discord.Interaction,
                  member: discord.Member,
                  reason: str = None):
        """Ban a member from the server."""
        await member.ban(reason=reason)

        embed = discord.Embed(
            title="Ban Command",
            description=f"{member} has been banned from the server.",
            color=discord.Color.red())
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)

        await interaction.response.send_message(embed=embed)
        await self.send_mod_message(interaction.user, "ban", reason)

    @app_commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self,
                   interaction: discord.Interaction,
                   member: discord.Member,
                   reason: str = None):
        """Kick a member from the server."""
        await member.kick(reason=reason)

        embed = discord.Embed(
            title="Kick Command",
            description=f"{member} has been kicked from the server.",
            color=discord.Color.orange())
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)

        await interaction.response.send_message(embed=embed)
        await self.send_mod_message(interaction.user, "kick", reason)

    @app_commands.command(name="mute")
    @commands.has_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction,
                   member: discord.Member, duration: int):
        """Mute a member for a specified duration."""
        mute_role = discord.utils.get(member.guild.roles, name="Muted")
        if mute_role:
            await member.add_roles(mute_role)
            embed = discord.Embed(
                title="Mute Command",
                description=f"{member} has been muted for {duration} minutes.",
                color=discord.Color.purple())
            embed.add_field(name="Duration",
                            value=f"{duration} minutes",
                            inline=False)
            await interaction.response.send_message(embed=embed)
            await self.send_mod_message(interaction.user, "mute",
                                        f"{duration} minutes")
        else:
            await interaction.response.send_message("Mute role not found.")

    @app_commands.command(name="warn")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, interaction: discord.Interaction,
                   member: discord.Member, *, reason: str):
        """Warn a member and send them a DM."""
        embed = discord.Embed(
            title="Warning",
            description=f"You have been warned by {interaction.user}.",
            color=discord.Color.yellow())
        embed.add_field(name="Reason", value=reason, inline=False)
        await member.send(embed=embed)

        embed = discord.Embed(title="Warn Command",
                              description=f"{member} has been warned.",
                              color=discord.Color.yellow())
        embed.add_field(name="Reason", value=reason, inline=False)
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
