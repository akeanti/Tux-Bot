import discord
from discord.ext import commands
import random
from discord import app_commands
from PIL import Image, ImageDraw, ImageFont
import io


class Cards(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.cards = {
            "Arch": {
                "desc":
                "<:arch:1278044002943504507> Arch Linux",
                "img":
                "https://c4.wallpaperflare.com/wallpaper/708/141/138/anime-anime-girls-technology-software-arch-linux-hd-wallpaper-preview.jpg"
            },
            "Ubuntu": {
                "desc":
                "<:ubuntu:1278050305359085629> Ubuntu",
                "img":
                "https://c4.wallpaperflare.com/wallpaper/905/587/596/technology-ubuntu-anime-wallpaper-preview.jpg"
            },
            "Fedora": {
                "desc":
                "<:fedora:1278050235909668955> Fedora",
                "img":
                "https://preview.redd.it/fedora-like-anime-girl-v0-yfabh380keha1.png?width=2560&format=png&auto=webp&s=cc3db47840395dfca9afc6aa60899c035a4d3d96"
            },
            "Debian": {
                "desc": "<:debian:1278050607495778387> Debian",
                "img": "https://wallpapercave.com/wp/wp6080117.jpg"
            },
            "Mint": {
                "desc":
                "<:mint:1278052689372254218> Linux Mint",
                "img":
                "https://i.flexichat.net/var/albums/linux-tan/linux_mint_tan_by_ditret-d3ips3e.png?m=1397664685"
            },
            "Gentoo": {
                "desc":
                "<:Gentoo:1278052921962922084> Gentoo",
                "img":
                "https://media.discordapp.net/attachments/1213837998366396508/1278048155686015088/maxresdefault1.png?ex=66cf6299&is=66ce1119&hm=cdc44a4d546e2fdc4428dcd90c41279f187de98f4412da8646bb77e6b181f673&=&format=webp&quality=lossless&width=687&height=373"
            },
            "Kali": {
                "desc": "<:kali:1278053771569795143> Kali Linux",
                "img": "https://wallpapercave.com/wp/wp6079876.jpg"
            },
            "CentOS": {
                "desc":
                "<:centos:1278054243349037117> CentOS",
                "img":
                "https://media.discordapp.net/attachments/1213837998366396508/1278049216450531422/ieB8CALTaDc-HD.jpg?ex=66cf6396&is=66ce1216&hm=f2e4bea416f426281cc6fb8aab51558d21ad7723c6ba96a064eff99411a759e7&=&format=webp&width=931&height=523"
            },
            "Slackware": {
                "desc":
                "<:slackware:1278054165129724058> Slackware",
                "img":
                "https://krita-artists.org/uploads/default/original/3X/9/e/9e0d94348b94095a7bba6f8ce7438ac043168a4e.jpeg"
            }
        }
        self.user_cards = {}
        self.user_xp = {}
        self.rare_card_prob = 0.02  # 2% chance to receive a rare card
        self.card_settings = {}  # Stores user-specific channel settings

    def _get_random_card(self):
        card_name, card_info = random.choice(list(self.cards.items()))
        if random.random() < self.rare_card_prob:
            card_name = random.choice(list(
                self.cards.keys()))  # Could be modified to return a rare card
        return card_name, card_info

    def _generate_level_image(self, user_name, xp, level):
        # Load custom background image
        bg_image = Image.open('level.png').convert('RGBA')
        width, height = bg_image.size

        # Create a drawing context
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        image.paste(bg_image, (0, 0), bg_image)

        d = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        # Draw text on the image
        d.text((10, 10),
               f"User: {user_name}",
               font=font,
               fill=(255, 255, 255, 255))
        d.text((10, 50), f"XP: {xp}", font=font, fill=(255, 255, 255, 255))
        d.text((10, 90),
               f"Level: {level}",
               font=font,
               fill=(255, 255, 255, 255))

        # Save the image to a bytes buffer
        buf = io.BytesIO()
        image.save(buf, format='PNG')
        buf.seek(0)
        return buf

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Check if the channel is enabled for card sending
        if not self.card_settings.get(str(message.channel.id), True):
            return

        if random.random() < 0.1:  # 10% chance to gain a card on each message
            card_name, card_info = self._get_random_card()
            user_id = str(message.author.id)
            if user_id not in self.user_cards:
                self.user_cards[user_id] = []
            self.user_cards[user_id].append(card_name)

            # Increment XP for the user
            if user_id not in self.user_xp:
                self.user_xp[user_id] = 0
            self.user_xp[
                user_id] += 10  # Increment XP by 10 for each card received

            # Determine the user level
            xp = self.user_xp[user_id]
            level = xp // 100  # Assuming 100 XP per level

            # Create an embed for the card message
            embed = discord.Embed(
                title="New Card Received!",
                description=
                f"{message.author.mention}, you have received a new card: **{card_info['desc']}**!\n\nIf you feel disturbed by the cards, you can use the `/toggle-cards` command to remove them from this channel.",
                color=discord.Color.blue())
            embed.set_image(url=card_info["img"])
            embed.set_footer(text=f"XP: {xp} | Level: {level}")

            await message.channel.send(embed=embed)

    @app_commands.command(name="user-profile",
                          description="View your profile with collected cards")
    async def user_profile(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        if user_id not in self.user_cards or not self.user_cards[user_id]:
            await interaction.response.send_message(
                f"{interaction.user.mention}, you don't have any cards yet!")
            return

        card_list = "\n".join([
            f"{self.cards[card]['desc']} {self.cards[card]['img']}"
            for card in self.user_cards[user_id]
        ])
        user_avatar = interaction.user.avatar_url
        embed = discord.Embed(title=f"{interaction.user.name}'s Profile",
                              description=card_list,
                              color=discord.Color.blue())
        embed.set_thumbnail(url=user_avatar)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="cards",
                          description="View your card collection")
    async def cards(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        if user_id not in self.user_cards or not self.user_cards[user_id]:
            await interaction.response.send_message(
                f"{interaction.user.mention}, you don't have any cards yet!")
            return

        card_list = "\n".join([
            f"{self.cards[card]['desc']} {self.cards[card]['img']}"
            for card in self.user_cards[user_id]
        ])
        embed = discord.Embed(title=f"{interaction.user.name}'s Cards",
                              description=card_list,
                              color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="exchange",
                          description="Exchange a card with another user")
    @app_commands.describe(member="The member you want to exchange cards with",
                           card_name="The card you want to exchange")
    async def exchange(self, interaction: discord.Interaction,
                       member: discord.Member, card_name: str):
        user_id = str(interaction.user.id)
        member_id = str(member.id)
        card_name = card_name.capitalize()

        if user_id not in self.user_cards or card_name not in self.user_cards[
                user_id]:
            await interaction.response.send_message(
                f"{interaction.user.mention}, you don't have the **{self.cards.get(card_name, {'desc': card_name})['desc']}** card to exchange!"
            )
            return

        if member_id not in self.user_cards:
            self.user_cards[member_id] = []

        self.user_cards[member_id].append(card_name)
        self.user_cards[user_id].remove(card_name)

        await interaction.response.send_message(
            f"{interaction.user.mention}, you have successfully exchanged your **{self.cards.get(card_name, {'desc': card_name})['desc']}** card with {member.mention}!"
        )

    @app_commands.command(
        name="toggle-cards",
        description="Enable or disable random card sending in this channel")
    async def toggle_cards(self, interaction: discord.Interaction):
        channel_id = str(interaction.channel.id)
        current_state = self.card_settings.get(channel_id, True)
        self.card_settings[channel_id] = not current_state
        state = "enabled" if not current_state else "disabled"
        await interaction.response.send_message(
            f"Random card sending has been {state} in this channel.")


async def setup(bot):
    await bot.add_cog(Cards(bot))
