import discord
from discord.ext import commands
import asyncio
import config


class TuxBot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix="/", intents=discord.Intents.all())
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
        cogs = [
            "cogs.moderation",
            "cogs.fun",
            "cogs.linux",
            "cogs.general",
            "cogs.cards",
            "cogs.ticket",
            "cogs.utility",
            "cogs.games",  # Load the new games cog
        ]
        for cog in cogs:
            await self.load_extension(cog)

    async def on_guild_join(self, guild):
        owner = guild.owner
        if owner:
            embed = discord.Embed(
                title="🎉 Thanks for Adding Us!",
                description=
                f"Thank you for adding Tux Bot to your server, **{guild.name}**! We're thrilled to be here.",
                color=discord.Color.orange())
            embed.set_thumbnail(
                url=
                "https://media.discordapp.net/attachments/1278052479308664884/1279518988224954488/shouko-nishimiya-arigato.gif?ex=66d4bc6b&is=66d36aeb&hm=749625411f78ec5b827638dbe553f4d841eadb22619852cec1c559dd6ea93786&=&width=622&height=330"
            )
            embed.set_footer(text="Tux Bot | Powered by Akeanti")

            button = discord.ui.Button(
                label="Visit Documentation",
                url="https://tux-discord-bot.github.io/Documentation/")
            view = discord.ui.View()
            view.add_item(button)

            try:
                await owner.send(embed=embed, view=view)
            except discord.Forbidden:
                print("Could not send DM to the guild owner.")


bot = TuxBot()
bot.run(config.TOKEN)
