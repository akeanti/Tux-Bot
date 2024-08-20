# cogs/general.py
import discord
from discord.ext import commands
from discord import app_commands


class General(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="TuxBot Commands",
            description="Here are all the commands you can use.",
            color=discord.Color.green())
        embed.add_field(name="/ban", value="Ban a user", inline=False)
        embed.add_field(name="/kick", value="Kick a user", inline=False)
        embed.add_field(name="/mute", value="Mute a user", inline=False)
        embed.add_field(name="/profile",
                        value="View a user's profile picture",
                        inline=False)
        embed.add_field(name="/neofetch",
                        value="Show a Linux-themed neofetch",
                        inline=False)
        embed.add_field(name="/linux",
                        value="List all Linux-themed commands",
                        inline=False)
        embed.set_footer(text="TuxBot - The Linux-themed Discord bot")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(General(bot))
