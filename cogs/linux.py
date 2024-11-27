import discord
from discord.ext import commands
from discord import app_commands
import random
import datetime


class Linux(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.datetime.utcnow()

    @app_commands.command(name="neofetch")
    async def neofetch(self, interaction: discord.Interaction):
        """Simulate the neofetch command."""
        output = """
        ```cmd
        ██████████████████  ███████   user@tux-bot
        ██████████████████  ███████   ---------------
        ████████           ████████   OS: Discord Linux
        ████████  ███████  ████████   Kernel: 5.11.0-38-generic
        ████████  ███████  ████████   Uptime: 5 hours, 32 mins
        ████████  ███████  ████████   Packages: 1800
        ████████  ███████  ████████   Shell: /bin/bash
        ████████  ███████  ████████   Terminal: Discord
        ████████  ███████  ████████   CPU: Virtual 2 Cores
        ████████  ███████  ████████   Memory: 512MB / 2048MB
        ```"""
        await interaction.response.send_message(output)

    @app_commands.command(name="uptime")
    async def uptime(self, interaction: discord.Interaction):
        """Shows the bot's uptime."""
        now = datetime.datetime.utcnow()
        delta = now - self.start_time
        days, seconds = delta.days, delta.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60

        # Creating the embed
        embed = discord.Embed(
            title="⏱️ Bot Uptime",
            description=f"**Uptime:**\n{days} days, {hours} hours, {minutes} minutes",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1213837998366396508/1275599997424898159/Tux1.png?ex=66c72352&is=66c5d1d2&hm=a62b7e526c922c85ded7e08a57186d5b41a971b5a611f9b244c7c7632a25bb11&=&format=webp&quality=lossless&width=523&height=523")  # Add a relevant thumbnail URL
        embed.set_footer(text="Keep it running! 🚀")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="fortune")
    async def fortune(self, interaction: discord.Interaction):
        """Simulate the fortune command."""
        fortunes = [
            "You will find great fortune in unexpected places.",
            "Beware of bugs in the code above; I have only proved it correct, not tried it.",
            "Good things come to those who wait.", "Fortune favors the bold.",
            "You will achieve your goals through perseverance."
        ]
        await interaction.response.send_message(
            f"Fortune: {random.choice(fortunes)}")

    @app_commands.command(name="cowthink")
    async def cowthink(self, interaction: discord.Interaction, message: str):
        """Simulate the cowthink command."""
        cow = f"""
        ```cmd
        {message}
          \\
           \\
             ^__^ 
             (oo)\\_______
             (__)\\       )\\/\\
                 ||----w |
                 ||     ||  
        ```
        """
        await interaction.response.send_message(cow)

    @app_commands.command(name="df")
    async def df(self, interaction: discord.Interaction):
        """Simulate the df (disk free) command."""
        df_output = """
        ```cmd
        Filesystem     1K-blocks    Used Available Use% Mounted on
        /dev/sda1       10485760  345234   10140526   4% /
        /dev/sda2       20971520  568231   20303289   3% /home
        /dev/sda3       31457280 1293812   30163468   5% /var
        ```
        """
        await interaction.response.send_message(df_output)

    @app_commands.command(name="top")
    async def top(self, interaction: discord.Interaction):
        """Simulate the top command to show running processes."""
        top_output = """
        ```cmd
        top - 15:21:07 up 1 day,  5:32,  1 user,  load average: 0.00, 0.01, 0.05
        Tasks: 192 total,   1 running, 191 sleeping,   0 stopped,   0 zombie
        %Cpu(s):  1.0 us,  0.5 sy,  0.0 ni, 98.0 id,  0.0 wa,  0.0 hi,  0.5 si,  0.0 st
        MiB Mem :  2048.0 total,   432.5 free,   945.3 used,   670.2 buff/cache
        MiB Swap:  1024.0 total,  1024.0 free,     0.0 used.   567.3 avail Mem 

          PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND
         1234 tuxbot    20   0  512000  94532  56732 S   1.0  4.6   0:01.27 python
         4321 tuxbot    20   0  256000  63250  31524 S   0.5  3.1   0:00.73 discord
        ```
        """
        await interaction.response.send_message(top_output)

    @app_commands.command(name="man")
    async def man(self, interaction: discord.Interaction, command: str):
        """Simulate the man command to show manual pages."""
        manuals = {
            "neofetch": "neofetch - Display system information in a colorful way",
            "uptime": "uptime - Show how long the system has been running",
            "fortune": "fortune - Display a random fortune message",
            "cowthink": "cowthink - Display a message inside a cow thinking bubble",
            "df": "df - Show disk space usage",
            "top": "top - Display a dynamic view of system processes",
        }
        response = manuals.get(command, "No manual entry for this command.")
        await interaction.response.send_message(
            f"Manual entry for `{command}`:\n{response}")

    @app_commands.command(name="linux")
    async def linux(self, interaction: discord.Interaction):
        """Shows all Linux-themed commands."""
        embed = discord.Embed(
            title="Linux Commands",
            description="List of available Linux-themed commands",
            color=discord.Color.blue())
        commands = [
            "/neofetch - Simulate the neofetch command",
            "/uptime - Show the bot's uptime",
            "/fortune - Simulate the fortune command",
            "/cowthink <message> - Simulate the cowthink command",
            "/df - Simulate the df (disk free) command",
            "/top - Simulate the top command",
            "/man <command> - Show manual page for a command",
        ]
        embed.add_field(name="Commands",
                        value="\n".join(commands),
                        inline=False)
        embed.set_footer(text="TuxBot - The Linux-themed Discord bot", icon_url="https://media.discordapp.net/attachments/1213837998366396508/1275599997424898159/Tux1.png?ex=66c67a92&is=66c52912&hm=992330999afdb3e9c48108fdfdfaad4b696c6042cc3bf807d3ddc3e95cd44de8&=&format=webp&quality=lossless&width=502&height=502")
        await interaction.response.send_message(embed=embed)


    # Additional Commands
    @app_commands.command(name="ls")
    async def ls(self, interaction: discord.Interaction):
        """Simulate the ls command."""
        ls_output = """
        ```cmd
        Desktop  Documents  Downloads  Music  Pictures  Videos
        ```
        """
        await interaction.response.send_message(ls_output)

    @app_commands.command(name="sl")
    async def sl(self, interaction: discord.Interaction):
        """Simulate the sl command."""
        embed = discord.Embed(title=f"user@tux-bot:~ $ sl", color=discord.Color.blue())
        embed.set_image(url="https://cdn.discordapp.com/attachments/1049614691091091507/1311117374291841084/sl.gif")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="whoami")
    async def whoami(self, interaction: discord.Interaction):
        """Simulate the whoami command."""
        whoami_output = """
        ```cmd
        tuxbot
        ```
        """
        await interaction.response.send_message(whoami_output)

    @app_commands.command(name="chmod")
    async def chmod(self, interaction: discord.Interaction, permissions: str, file: str):
        """Simulate the chmod command."""
        chmod_output = f"""
        ```cmd
        Changing permissions of '{file}' to '{permissions}'
        ```
        """
        await interaction.response.send_message(chmod_output)

    @app_commands.command(name="grep")
    async def grep(self, interaction: discord.Interaction, pattern: str, file: str):
        """Simulate the grep command."""
        grep_output = f"""
        ```cmd
        Searching for '{pattern}' in '{file}'
        No matches found.
        ```
        """
        await interaction.response.send_message(grep_output)

    @app_commands.command(name="ping")
    async def ping(self, interaction: discord.Interaction):
        """Simulate the ping command."""
        ping_output = """
        ```cmd
        PING example.com (93.184.216.34) 56(84) bytes of data.
        64 bytes from example.com (93.184.216.34): icmp_seq=1 ttl=56 time=14.2 ms
        ```
        """
        await interaction.response.send_message(ping_output)

    @app_commands.command(name="ps")
    async def ps(self, interaction: discord.Interaction):
        """Simulate the ps command."""
        ps_output = """
        ```cmd
        PID TTY          TIME CMD
        1234 pts/0    00:00:01 bash
        5678 pts/0    00:00:00 python
        ```
        """
        await interaction.response.send_message(ps_output)

    @app_commands.command(name="kill")
    async def kill(self, interaction: discord.Interaction, pid: int):
        """Simulate the kill command."""
        kill_output = f"""
        ```cmd
        Sending SIGTERM to process {pid}
        Process {pid} terminated.
        ```
        """
        await interaction.response.send_message(kill_output)

    @app_commands.command(name="card")
    async def card(self, interaction: discord.Interaction):
        """Send a cool Linux-themed card with kernel info as an embed."""

        # Create an embed
        embed = discord.Embed(
            title="Linux Kernel Card",
            color=discord.Color.blue()
        )
        embed.set_image(url="https://media.discordapp.net/attachments/1275615408933834844/1275955481633886371/svgviewer-png-output.png?ex=66c7c5a4&is=66c67424&hm=6cd16cddbdbedc825e8762ad164f201130ef0d3203554ebea049732c2b1c5f38&=&format=webp&quality=lossless&width=392&height=523")
        embed.set_footer(text="TuxBot - The Linux-themed Discord bot", icon_url="https://media.discordapp.net/attachments/1213837998366396508/1275599997424898159/Tux1.png?ex=66c67a92&is=66c52912&hm=992330999afdb3e9c48108fdfdfaad4b696c6042cc3bf807d3ddc3e95cd44de8&=&format=webp&quality=lossless&width=502&height=502")
        # Send the embed
        await interaction.response.send_message(embed=embed)




async def setup(bot):
    await bot.add_cog(Linux(bot))
