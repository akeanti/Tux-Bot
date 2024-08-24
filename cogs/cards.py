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
                "desc": "🟦 Arch Linux",
                "img": "https://example.com/arch.png"
            },
            "Ubuntu": {
                "desc": "🟧 Ubuntu",
                "img": "https://example.com/ubuntu.png"
            },
            "Fedora": {
                "desc": "🟦 Fedora",
                "img": "https://example.com/fedora.png"
            },
            "Debian": {
                "desc": "🟥 Debian",
                "img": "https://example.com/debian.png"
            },
            "Mint": {
                "desc": "🟩 Linux Mint",
                "img": "https://example.com/mint.png"
            },
            "Gentoo": {
                "desc": "🟪 Gentoo",
                "img": "https://example.com/gentoo.png"
            },
            "Kali": {
                "desc": "🟥 Kali Linux",
                "img": "https://example.com/kali.png"
            },
            "CentOS": {
                "desc": "🟦 CentOS",
                "img": "https://example.com/centos.png"
            },
            "Slackware": {
                "desc": "🟦 Slackware",
                "img": "https://example.com/slackware.png"
            }
        }
        self.user_cards = {}
        self.user_xp = {}
        self.rare_card_prob = 0.02  # 2% chance to receive a rare card

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

            await message.channel.send(
                f"{message.author.mention}, you have received a new card: **{card_info['desc']}**! {card_info['img']}"
            )

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

        self.user_cards[user_id].remove(card_name)
        self.user_cards[member_id].append(card_name)

        await interaction.response.send_message(
            f"{interaction.user.mention} has exchanged **{self.cards[card_name]['desc']}** with {member.mention}!"
        )

    @app_commands.command(name="gift",
                          description="Gift a card to another user")
    @app_commands.describe(member="The member you want to gift a card to",
                           card_name="The card you want to gift")
    async def gift(self, interaction: discord.Interaction,
                   member: discord.Member, card_name: str):
        user_id = str(interaction.user.id)
        member_id = str(member.id)
        card_name = card_name.capitalize()

        if user_id not in self.user_cards or card_name not in self.user_cards[
                user_id]:
            await interaction.response.send_message(
                f"{interaction.user.mention}, you don't have the **{self.cards.get(card_name, {'desc': card_name})['desc']}** card to gift!"
            )
            return

        if member_id not in self.user_cards:
            self.user_cards[member_id] = []

        self.user_cards[user_id].remove(card_name)
        self.user_cards[member_id].append(card_name)

        await interaction.response.send_message(
            f"{interaction.user.mention} has gifted **{self.cards[card_name]['desc']}** to {member.mention}!"
        )

    @app_commands.command(name="steal",
                          description="Steal a card from another user")
    @app_commands.describe(member="The member you want to steal a card from")
    async def steal(self, interaction: discord.Interaction,
                    member: discord.Member):
        user_id = str(interaction.user.id)
        member_id = str(member.id)

        if member_id not in self.user_cards or not self.user_cards[member_id]:
            await interaction.response.send_message(
                f"{member.mention} doesn't have any cards to steal!")
            return

        stolen_card = random.choice(self.user_cards[member_id])
        self.user_cards[member_id].remove(stolen_card)

        if user_id not in self.user_cards:
            self.user_cards[user_id] = []

        self.user_cards[user_id].append(stolen_card)

        await interaction.response.send_message(
            f"{interaction.user.mention} has stolen **{self.cards[stolen_card]['desc']}** from {member.mention}!"
        )

    @app_commands.command(name="card-help",
                          description="List all card commands")
    async def card_help(self, interaction: discord.Interaction):
        help_text = (
            "/cards - View your card collection\n"
            "/user-profile - View your profile with collected cards\n"
            "/exchange [member] [card_name] - Exchange a card with another user\n"
            "/gift [member] [card_name] - Gift a card to another user\n"
            "/steal [member] - Steal a card from another user\n"
            "/card-help - Show this help message")
        embed = discord.Embed(title="Card Commands Help",
                              description=help_text,
                              color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="level", description="View your level and XP")
    async def level(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        xp = self.user_xp.get(user_id, 0)
        level = xp // 100  # Assuming 100 XP per level

        # Generate level image
        level_image = self._generate_level_image(interaction.user.name, xp,
                                                 level)

        # Send level image
        file = discord.File(level_image, filename="level.png")
        embed = discord.Embed(title=f"{interaction.user.name}'s Level",
                              color=discord.Color.blue())
        embed.set_image(url="attachment://level.png")
        await interaction.response.send_message(embed=embed, file=file)


async def setup(bot):
    await bot.add_cog(Cards(bot))
