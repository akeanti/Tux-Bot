import discord
from discord.ext import commands
from discord import app_commands
import random
import datetime


class Fun(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.afk_users = {}  # Dictionary to store AFK statuses

    @app_commands.command(name="profile")
    async def profile(self,
                      interaction: discord.Interaction,
                      member: discord.Member = None):
        member = member or interaction.user
        embed = discord.Embed(title=f"{member}'s Profile",
                              color=discord.Color.blue())
        embed.set_image(url=member.avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="invite")
    async def invite(self, interaction: discord.Interaction):
        """Displays an embed with invite link, support server, and webpage links."""
        embed = discord.Embed(title="Support Us",
                              description="Use our bot and support us!",
                              color=discord.Color.green())
        embed.add_field(
            name="Invite the Bot",
            value=
            "[Click here to invite the bot](YOUR_BOT_INVITE_LINK)",  # Replace with your bot invite link
            inline=False)
        embed.add_field(
            name="Support Server",
            value=
            "[Join our support server](YOUR_SUPPORT_SERVER_LINK)",  # Replace with your support server link
            inline=False)
        embed.add_field(
            name="Our Webpage",
            value=
            "[Visit our webpage](YOUR_WEBPAGE_LINK)",  # Replace with your webpage link
            inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="sauce")
    async def sauce(self, interaction: discord.Interaction):
        """Provides an embed with a link to the GitHub repository."""
        embed = discord.Embed(
            title="GitHub Repository",
            description="Check out the source code of this bot on GitHub!",
            color=discord.Color.blue())
        embed.add_field(
            name="Repository",
            value=
            "[Click here to view the repo](YOUR_GITHUB_REPO_LINK)",  # Replace with your GitHub repo link
            inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="see_logo")
    async def see_logo(self, interaction: discord.Interaction):
        """Displays the server's icon/logo."""
        guild = interaction.guild
        if guild.icon:
            embed = discord.Embed(title=f"{guild.name}'s Logo",
                                  color=discord.Color.blue())
            embed.set_image(url=guild.icon.url)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                "This server does not have a logo.")

    @app_commands.command(name="meme")
    async def meme(self, interaction: discord.Interaction):
        """Fetches a random meme."""
        # You can use an API or a predefined list for memes. This is a placeholder.
        memes = [
            "https://i.imgur.com/4Wn16h7.jpg",
            "https://i.imgur.com/4pLeA0t.jpg",
            "https://i.imgur.com/Fkj1XFR.jpg"
        ]
        meme_url = random.choice(memes)
        embed = discord.Embed(title="Here's a meme for you!",
                              color=discord.Color.purple())
        embed.set_image(url=meme_url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="remind")
    async def remind(self, interaction: discord.Interaction, time: int, *,
                     message: str):
        """Sets a reminder with a message after a specified time in minutes."""
        await interaction.response.send_message(
            f"Reminder set for {time} minutes.")

        # Convert minutes to seconds
        await discord.utils.sleep_until(datetime.datetime.now() +
                                        datetime.timedelta(minutes=time))
        await interaction.user.send(f"Reminder: {message}")

    @app_commands.command(name="serverstats")
    async def serverstats(self, interaction: discord.Interaction):
        """Displays server statistics."""
        guild = interaction.guild
        total_members = guild.member_count
        online_members = len(
            [m for m in guild.members if m.status == discord.Status.online])

        embed = discord.Embed(title="Server Statistics",
                              color=discord.Color.blue())
        embed.add_field(name="Total Members",
                        value=total_members,
                        inline=False)
        embed.add_field(name="Online Members",
                        value=online_members,
                        inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="afk")
    async def afk(self,
                  interaction: discord.Interaction,
                  *,
                  reason: str = "AFK"):
        """Sets the user as AFK with an optional reason."""
        self.afk_users[interaction.user.id] = reason
        await interaction.response.send_message(f"You are now AFK: {reason}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Checks if a user is mentioned and notifies them if they are AFK."""
        if message.author.bot:
            return

        # Notify AFK users if they are mentioned
        mentioned_users = [
            user for user in message.mentions if user.id in self.afk_users
        ]
        for user in mentioned_users:
            reason = self.afk_users.get(user.id, "No reason provided.")
            await message.channel.send(f"{user.mention} is AFK: {reason}")

        # Remove AFK status if the user sends a message
        if message.author.id in self.afk_users:
            reason = self.afk_users.pop(message.author.id)
            await message.channel.send(
                f"{message.author.mention}, your AFK status has been removed. You were away because: {reason}"
            )


async def setup(bot):
    await bot.add_cog(Fun(bot))