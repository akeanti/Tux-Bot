# bot.py
import discord
from discord.ext import commands
import asyncio
import config


class TuxBot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())
        self.status_cycle = [
            "playing with Linux", "destroying Windows",
            "use /help to get started..."
        ]

    async def on_ready(self):
        await self.load_cogs()
        await self.tree.sync()  # Force sync commands globally on bot startup
        print(f'{self.user} has connected to Discord!')
        print('Commands synced.')
        asyncio.create_task(self.cycle_status())

    async def cycle_status(self):
        while True:
            for status in self.status_cycle:
                await self.change_presence(activity=discord.Game(status))
                await asyncio.sleep(60)

    async def load_cogs(self):
        cogs = ["cogs.moderation", "cogs.fun", "cogs.linux", "cogs.general"]
        for cog in cogs:
            await self.load_extension(cog)

    async def setup(bot):
        await bot.add_cog(Linux(bot))
        print('Linux cog loaded.')


bot = TuxBot()
bot.run(config.TOKEN)
