import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.ui import View, Button
import random
import datetime
import asyncio


class Fun(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.afk_users = {}  # Dictionary to store AFK statuses
        self.server_activity = {}  # Dictionary to store server activity
        self.max_top_servers = 5  # Limit to the number of top servers to show

        # Schedule periodic cleanup
        self.cleanup_loop.start()

    @app_commands.command(name="profile")
    async def profile(self,
                      interaction: discord.Interaction,
                      member: discord.Member = None):
        """Displays the profile of a member with their avatar."""
        member = member or interaction.user
        embed = discord.Embed(title=f"{member.name}'s Profile",
                              color=discord.Color.blue())
        embed.set_thumbnail(url=member.avatar.url)
        embed.add_field(name="Username", value=member.name, inline=True)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.set_footer(text="Profile Information")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="invite")
    async def invite(self, interaction: discord.Interaction):
        """Displays an embed with invite link, support server, and webpage links."""
        embed = discord.Embed(
            title="Support Us",
            description="Help us grow and support our project!",
            color=discord.Color.green())
        embed.add_field(
            name="Invite the Bot",
            value=
            "[Click here to invite the bot](https://discord.com/oauth2/authorize?client_id=1275464978207604856)",
            inline=False)
        embed.add_field(
            name="Support Server",
            value="[Join our support server](https://discord.gg/A2rQsnQMvy)",
            inline=False)
        embed.add_field(
            name="Our Webpage",
            value="[Visit our webpage](https://tux-discord-bot.github.io/)",
            inline=False)
        embed.set_footer(text="Thank you for your support!")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="sauce")
    async def sauce(self, interaction: discord.Interaction):
        """Provides a link to the GitHub repository."""
        embed = discord.Embed(
            title="GitHub Repository",
            description="Check out the source code of this bot on GitHub!",
            color=discord.Color.blue())
        embed.add_field(
            name="Repository",
            value=
            "[Click here to view the repo](https://github.com/akeanti/Tux-Bot)",
            inline=False)
        embed.set_footer(text="Open source and community-driven")
        embed.set_thumbnail(
            url=
            "https://media.discordapp.net/attachments/1213837998366396508/1275599997424898159/Tux1.png?ex=66c67a92&is=66c52912&hm=992330999afdb3e9c48108fdfdfaad4b696c6042cc3bf807d3ddc3e95cd44de8&=&format=webp&quality=lossless&width=502&height=502"
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="see_logo")
    async def see_logo(self, interaction: discord.Interaction):
        """Displays the server's icon/logo."""
        guild = interaction.guild
        if guild.icon:
            embed = discord.Embed(title=f"{guild.name}'s Logo",
                                  color=discord.Color.blue())
            embed.set_image(url=guild.icon.url)
            embed.set_footer(text="Server Logo")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                "This server does not have a logo.")

    @app_commands.command(name="meme")
    async def meme(self, interaction: discord.Interaction):
        """Fetches and displays a random meme."""
        memes = [
            "https://www.meyerperin.com/images/arch-fly.webp",
            "https://www.meyerperin.com/images/arch-merits.jpg",
            "https://www.linux.org/attachments/an-update-is-available-for-your-computer-linux-windows-mac_o_93777-jpg.8998/",
            "https://miro.medium.com/v2/resize:fit:1280/format:webp/0*sbY2fUKYGlcCD31C.jpeg"
        ]
        meme_url = random.choice(memes)
        embed = discord.Embed(title="Here's a Meme for You!",
                              color=discord.Color.purple())
        embed.set_image(url=meme_url)
        embed.set_footer(text="Enjoy the meme!")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="remind")
    async def remind(self, interaction: discord.Interaction, time: int, *,
                     message: str):
        """Sets a reminder with a message after a specified time in minutes."""
        await interaction.response.send_message(
            f"Reminder set for {time} minutes.")

        # Convert minutes to seconds
        await asyncio.sleep(time * 60)
        await interaction.user.send(f"Reminder: {message}")

    @app_commands.command(name="afk")
    async def afk(self,
                  interaction: discord.Interaction,
                  *,
                  reason: str = "AFK"):
        """Sets the user as AFK with an optional reason."""
        self.afk_users[interaction.user.id] = reason
        embed = discord.Embed(title="AFK Status",
                              description=f"You are now AFK: {reason}",
                              color=discord.Color.orange())
        embed.set_footer(text="AFK Mode Activated")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="list_servers")
    async def list_servers(self, interaction: discord.Interaction):
        """Lists all servers the bot is in with pagination and server icons."""
        guilds = self.bot.guilds
        per_page = 10
        pages = [
            guilds[i:i + per_page] for i in range(0, len(guilds), per_page)
        ]

        embed = self.create_embed(pages[0], 1, len(pages))
        view = ServerListView(pages, 1, self.create_embed)
        await interaction.response.send_message(embed=embed, view=view)

    def create_embed(self, guilds, current_page, total_pages):
        """Helper method to create an embed for the current page of servers."""
        embed = discord.Embed(
            title=f"Servers I'm In - Page {current_page}/{total_pages}",
            color=discord.Color.gold())
        for guild in guilds:
            icon_url = guild.icon.url if guild.icon else "https://via.placeholder.com/100"
            embed.add_field(name=guild.name,
                            value=f"Members: {guild.member_count}",
                            inline=False)
            embed.set_thumbnail(url=icon_url)
        embed.set_footer(text=f"Page {current_page} of {total_pages}")
        return embed

    @app_commands.command(name="top_servers")
    async def top_servers(self, interaction: discord.Interaction):
        """Displays top servers based on activity."""
        sorted_servers = sorted(self.server_activity.items(),
                                key=lambda x: x[1],
                                reverse=True)
        top_servers = sorted_servers[:self.
                                     max_top_servers]  # Limit to top servers
        embed = discord.Embed(title="Top Servers Based on Activity",
                              color=discord.Color.gold())

        for rank, (guild_id, activity) in enumerate(top_servers, start=1):
            guild = self.bot.get_guild(guild_id)
            if guild:
                embed.add_field(
                    name=f"{rank}. {guild.name}",
                    value=
                    f"Members: {guild.member_count} | Activity Score: {activity}",
                    inline=False)

        if not top_servers:
            embed.description = "No server activity data available."

        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Checks if a user is mentioned and notifies them if they are AFK."""
        if message.author.bot:
            return

        # Update server activity (simple example, use actual metrics in production)
        guild_id = message.guild.id
        if guild_id in self.server_activity:
            self.server_activity[guild_id] += 1
        else:
            self.server_activity[guild_id] = 1

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

    @tasks.loop(hours=24)
    async def cleanup_loop(self):
        """Periodic cleanup of old data."""
        # Example cleanup logic: Remove entries older than 30 days
        threshold = datetime.datetime.now() - datetime.timedelta(days=30)
        self.server_activity = {
            k: v
            for k, v in self.server_activity.items() if v >= threshold
        }


class ServerListView(View):

    def __init__(self, pages, current_page, create_embed):
        super().__init__(timeout=None)
        self.pages = pages
        self.current_page = current_page
        self.create_embed = create_embed

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def previous_button(self, interaction: discord.Interaction,
                              button: Button):
        if self.current_page > 1:
            self.current_page -= 1
            embed = self.create_embed(self.pages[self.current_page - 1],
                                      self.current_page, len(self.pages))
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction,
                          button: Button):
        if self.current_page < len(self.pages):
            self.current_page += 1
            embed = self.create_embed(self.pages[self.current_page - 1],
                                      self.current_page, len(self.pages))
            await interaction.response.edit_message(embed=embed, view=self)


async def setup(bot):
    await bot.add_cog(Fun(bot))
