import discord
from discord.ext import commands
from discord import app_commands
import random
import datetime
import aiohttp


class Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="avatar")
    async def avatar(self,
                     interaction: discord.Interaction,
                     member: discord.Member = None):
        """Displays the avatar of a member."""
        member = member or interaction.user
        embed = discord.Embed(title=f"{member}'s Avatar",
                              color=discord.Color.green())
        embed.set_image(url=member.avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo")
    async def serverinfo(self, interaction: discord.Interaction):
        """Displays information about the server."""
        guild = interaction.guild
        embed = discord.Embed(title=f"Server Info: {guild.name}",
                              color=discord.Color.blue())
        embed.add_field(name="Server ID", value=guild.id, inline=False)
        embed.add_field(name="Owner", value=guild.owner, inline=True)
        embed.add_field(name="Region", value=str(guild.region), inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Created At",
                        value=guild.created_at.strftime("%b %d, %Y"),
                        inline=True)
        embed.set_thumbnail(url=guild.icon.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo")
    async def userinfo(self,
                       interaction: discord.Interaction,
                       member: discord.Member = None):
        """Displays information about a member."""
        member = member or interaction.user
        embed = discord.Embed(title=f"User Info: {member.name}",
                              color=discord.Color.orange())
        embed.add_field(name="Username", value=member.name, inline=True)
        embed.add_field(name="Discriminator",
                        value=member.discriminator,
                        inline=True)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Joined Server",
                        value=member.joined_at.strftime("%b %d, %Y"),
                        inline=True)
        embed.add_field(name="Joined Discord",
                        value=member.created_at.strftime("%b %d, %Y"),
                        inline=True)
        embed.set_thumbnail(url=member.avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="choose")
    async def choose(self, interaction: discord.Interaction, *choices: str):
        """Randomly choose between given choices."""
        if not choices:
            await interaction.response.send_message(
                "You need to provide at least one choice.")
            return
        choice = random.choice(choices)
        await interaction.response.send_message(f"I choose: {choice}")

    @app_commands.command(name="weather")
    async def weather(self, interaction: discord.Interaction, city: str):
        """Get the current weather for a city."""
        api_key = 'YOUR_OPENWEATHER_API_KEY'  # Replace with your API key
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            ) as resp:
                data = await resp.json()
                if data.get('cod') != 200:
                    await interaction.response.send_message("City not found.")
                    return

                weather_description = data['weather'][0]['description']
                temp = data['main']['temp']
                city_name = data['name']

                embed = discord.Embed(title=f"Weather in {city_name}",
                                      color=discord.Color.blue())
                embed.add_field(name="Temperature",
                                value=f"{temp}°C",
                                inline=True)
                embed.add_field(name="Description",
                                value=weather_description.capitalize(),
                                inline=True)
                await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverstats")
    async def serverstats(self, interaction: discord.Interaction):
        """Display server statistics like active users, bots, etc."""
        guild = interaction.guild
        online_members = sum(member.status == discord.Status.online
                             for member in guild.members)
        total_members = guild.member_count
        bot_count = sum(member.bot for member in guild.members)

        embed = discord.Embed(title="Server Statistics",
                              color=discord.Color.green())
        embed.add_field(name="Total Members", value=total_members, inline=True)
        embed.add_field(name="Online Members",
                        value=online_members,
                        inline=True)
        embed.add_field(name="Bots", value=bot_count, inline=True)
        embed.add_field(name="Humans",
                        value=total_members - bot_count,
                        inline=True)
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Utility(bot))
