import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio


class LinuxGames(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def wait_for_message(self, interaction, timeout=30.0):

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        try:
            msg = await self.bot.wait_for('message',
                                          timeout=timeout,
                                          check=check)
            return msg
        except asyncio.TimeoutError:
            await interaction.followup.send('⏳ You took too long!')
            return None

    @app_commands.command(name='race',
                          description="Start a text-based racing game")
    async def race(self, interaction: discord.Interaction):
        """Start a text-based racing game"""
        await interaction.response.send_message(
            "🏁 Welcome to the Linux Racing Game! 🚀 Type 'start' to begin.")

        msg = await self.wait_for_message(interaction)
        if msg and msg.content.lower() == 'start':
            await interaction.followup.send("🚦 3... 2... 1... Go!")
            await asyncio.sleep(random.randint(1, 5))
            await interaction.followup.send("🎉 You crossed the finish line! 🏁")
        elif msg:
            await interaction.followup.send(
                "❌ Race cancelled. Type 'start' to try again.")

    @app_commands.command(name='trivia',
                          description="Start a Linux-themed trivia quiz")
    async def trivia(self, interaction: discord.Interaction):
        """Start a Linux-themed trivia quiz"""
        questions = {
            "🧠 What is the kernel of the Linux operating system?": "Linux",
            "🤔 Who is the creator of the Linux kernel?": "Linus Torvalds",
            "📂 What is the command to list files in a directory?": "ls",
            "📁 Which command is used to change directory?": "cd"
        }

        question, answer = random.choice(list(questions.items()))
        await interaction.response.send_message(question)

        msg = await self.wait_for_message(interaction)
        if msg:
            if msg.content.lower() == answer.lower():
                await interaction.followup.send('✅ Correct!')
            else:
                await interaction.followup.send(
                    f'❌ Wrong answer. The correct answer was: {answer}')

    @app_commands.command(name='guess', description="A number guessing game")
    async def guess(self, interaction: discord.Interaction):
        """A number guessing game"""
        number = random.randint(1, 10)
        await interaction.response.send_message(
            "🎲 Guess a number between 1 and 10.")

        msg = await self.wait_for_message(interaction)
        if msg:
            try:
                guess = int(msg.content)
                if guess == number:
                    await interaction.followup.send(
                        '🎉 Congratulations! You guessed it right!')
                else:
                    await interaction.followup.send(
                        f'❌ Sorry, the correct number was {number}. Better luck next time!'
                    )
            except ValueError:
                await interaction.followup.send(
                    '🚫 Please enter a valid number.')

    @app_commands.command(name='hangman',
                          description="Play a word-guessing game")
    async def hangman(self, interaction: discord.Interaction):
        """Play a word-guessing game"""
        words = ["linux", "kernel", "command", "terminal", "ubuntu"]
        word = random.choice(words)
        guessed_letters = set()
        attempts = 6

        def get_display_word():
            return ' '.join(letter if letter in guessed_letters else '_'
                            for letter in word)

        await interaction.response.send_message(
            f"📝 Let's play Hangman! You have {attempts} attempts left.")
        await interaction.followup.send(f"Word: {get_display_word()}")

        while attempts > 0 and set(word) != guessed_letters:
            msg = await self.wait_for_message(interaction)
            if msg:
                letter = msg.content.lower()

                if len(letter) != 1 or not letter.isalpha():
                    await interaction.followup.send(
                        '🚫 Please enter a single letter.')
                    continue

                if letter in guessed_letters:
                    await interaction.followup.send(
                        '🔄 You already guessed that letter.')
                    continue

                guessed_letters.add(letter)

                if letter in word:
                    await interaction.followup.send(
                        f'✅ Good guess! {get_display_word()}')
                else:
                    attempts -= 1
                    await interaction.followup.send(
                        f'❌ Wrong guess! {get_display_word()}. Attempts left: {attempts}'
                    )

                if set(word) == guessed_letters:
                    await interaction.followup.send(
                        f'🎉 Congratulations! You guessed the word: {word}')
                elif attempts == 0:
                    await interaction.followup.send(
                        f'💥 Game over! The word was: {word}')

    @app_commands.command(name='rock-paper-scissors',
                          description="Play Rock, Paper, Scissors")
    async def rock_paper_scissors(self, interaction: discord.Interaction,
                                  choice: str):
        """Play Rock, Paper, Scissors"""
        choices = ["rock", "paper", "scissors"]
        bot_choice = random.choice(choices)
        user_choice = choice.lower()

        if user_choice not in choices:
            await interaction.response.send_message(
                "❌ Invalid choice! Please choose rock, paper, or scissors.")
            return

        result = self.determine_rps_winner(user_choice, bot_choice)
        await interaction.response.send_message(
            f"🤖 Bot chose: {bot_choice}\n{result}")

    def determine_rps_winner(self, user_choice, bot_choice):
        if user_choice == bot_choice:
            return "It's a tie!"
        elif (user_choice == "rock" and bot_choice == "scissors") or \
             (user_choice == "paper" and bot_choice == "rock") or \
             (user_choice == "scissors" and bot_choice == "paper"):
            return "🎉 You win!"
        else:
            return "❌ You lose!"

    @app_commands.command(name='wordsearch',
                          description="Solve a word search puzzle")
    async def wordsearch(self, interaction: discord.Interaction):
        """Solve a word search puzzle"""
        words = ["linux", "kernel", "command", "terminal"]
        puzzle = self.generate_wordsearch(words)
        await interaction.response.send_message(
            f"🔍 Solve this word search puzzle:\n\n{puzzle}")

    def generate_wordsearch(self, words):
        grid_size = 10
        grid = [[' ' for _ in range(grid_size)] for _ in range(grid_size)]

        for word in words:
            direction = random.choice(['H', 'V'])
            start_row = random.randint(0, grid_size - 1)
            start_col = random.randint(0, grid_size - 1)

            if direction == 'H':
                if start_col + len(word) <= grid_size:
                    for i, letter in enumerate(word):
                        grid[start_row][start_col + i] = letter
            elif direction == 'V':
                if start_row + len(word) <= grid_size:
                    for i, letter in enumerate(word):
                        grid[start_row + i][start_col] = letter

        return '\n'.join(' '.join(row) for row in grid)

    @app_commands.command(name='connect-four', description="Play Connect Four against the bot")
    async def connect_four(self, interaction: discord.Interaction):
        """Play Connect Four against the bot"""
        board = [['⚪' for _ in range(7)] for _ in range(6)]
        player = '🔴'
        bot = '🟡'
        winner = None

        def print_board():
            return '\n'.join([' '.join(row) for row in board])

        def drop_piece(col, piece):
            for row in reversed(board):
                if row[col] == '⚪':
                    row[col] = piece
                    break

        def check_winner():

            def check_line(line):
                for i in range(len(line) - 3):
                    if line[i] == line[i + 1] == line[i + 2] == line[i +
                                                                     3] != '⚪':
                        return line[i]
                return None

            # Check rows
            for row in board:
                winner = check_line(row)
                if winner:
                    return winner

            # Check columns
            for col in range(7):
                column = [board[row][col] for row in range(6)]
                winner = check_line(column)
                if winner:
                    return winner

            # Check diagonals
            for row in range(6):
                for col in range(7):
                    diagonal1 = [
                        board[row + i][col + i] for i in range(4)
                        if row + i < 6 and col + i < 7
                    ]
                    diagonal2 = [
                        board[row + i][col - i] for i in range(4)
                        if row + i < 6 and col - i >= 0
                    ]
                    if check_line(diagonal1):
                        return check_line(diagonal1)
                    if check_line(diagonal2):
                        return check_line(diagonal2)

            return None

        def is_full():
            return all(board[0][col] != '⚪' for col in range(7))

        await interaction.response.send_message(
            f"🟡 Connect Four! {interaction.user.name}, you're playing as 🔴. Here's the board:\n\n{print_board()}"
        )

        while not winner and not is_full():
            await interaction.followup.send(
                f"{interaction.user.name}, choose a column (0-6) to drop your piece."
            )

            msg = await self.wait_for_message(interaction)
            if msg:
                try:
                    col = int(msg.content)
                    if col < 0 or col > 6:
                        await interaction.followup.send(
                            '🚫 Invalid column! Please choose a column between 0 and 6.'
                        )
                        continue
                    if board[0][col] != '⚪':
                        await interaction.followup.send(
                            '🚫 Column is full! Choose another column.')
                        continue

                    drop_piece(col, player)
                    winner = check_winner()
                    if winner:
                        break

                    # Bot move
                    bot_col = random.choice(
                        [i for i in range(7) if board[0][i] == '⚪'])
                    drop_piece(bot_col, bot)
                    winner = check_winner()

                    await interaction.followup.send(f"🟡 Bot dropped a piece in column {bot_col}.")
                    await interaction.followup.send(f"Current board:\n\n{print_board()}")

                except ValueError:
                    await interaction.followup.send(
                        '🚫 Please enter a valid column number.')

        if winner:
            if winner == player:
                await interaction.followup.send(
                    f"🎉 Congratulations {interaction.user.name}! You won!")
            else:
                await interaction.followup.send("💥 The bot won! Better luck next time!")
        else:
            await interaction.followup.send("It's a tie!")


    @app_commands.command(name='tic-tac-toe', description="Play a game of Tic-Tac-Toe")
    async def tic_tac_toe(self, interaction: discord.Interaction):
        """Play a game of Tic-Tac-Toe"""

        board = ['⬛'] * 9
        player = '❌'
        bot = '⭕'

        def print_board():
            return f"{board[0]} | {board[1]} | {board[2]}\n" \
                   f"{board[3]} | {board[4]} | {board[5]}\n" \
                   f"{board[6]} | {board[7]} | {board[8]}"

        def check_winner(b):
            win_conditions = [
                [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
                [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
                [0, 4, 8], [2, 4, 6]  # Diagonals
            ]
            for condition in win_conditions:
                if b[condition[0]] == b[condition[1]] == b[condition[2]] != '⬛':
                    return b[condition[0]]
            return None

        async def player_move():
            embed = discord.Embed(title="Tic-Tac-Toe", description=f"{interaction.user.name}, choose a position (0-8):\n{print_board()}", color=discord.Color.blue())
            await interaction.followup.send(embed=embed)
            msg = await self.bot.wait_for('message', check=lambda m: m.author == interaction.user and m.channel == interaction.channel)
            if msg:
                try:
                    pos = int(msg.content)
                    if board[pos] != '⬛':
                        await interaction.followup.send("🚫 Position already taken! Try again.")
                        return await player_move()
                    board[pos] = player
                except (ValueError, IndexError):
                    await interaction.followup.send("🚫 Invalid position! Choose a number between 0-8.")
                    return await player_move()

        def bot_move():
            available_moves = [i for i in range(9) if board[i] == '⬛']
            bot_choice = random.choice(available_moves)
            board[bot_choice] = bot

        winner = None

        await interaction.response.send_message(embed=discord.Embed(title="Tic-Tac-Toe", description="🎮 Let's play Tic-Tac-Toe!", color=discord.Color.green()))

        while not winner and '⬛' in board:
            await player_move()
            winner = check_winner(board)
            if winner or '⬛' not in board:
                break

            bot_move()
            winner = check_winner(board)

        embed = discord.Embed(title="Tic-Tac-Toe Result", description=print_board(), color=discord.Color.red())
        if winner:
            if winner == player:
                embed.add_field(name="Result", value=f"🎉 {interaction.user.name} wins!")
            else:
                embed.add_field(name="Result", value="💥 Bot wins!")
        else:
            embed.add_field(name="Result", value="It's a tie!")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name='snake',
                          description="Play a text-based Snake game")
    async def snake(self, interaction: discord.Interaction):
        """Play a text-based Snake game"""
        await interaction.response.send_message(
            "🐍 Snake game is under construction. Stay tuned!")

    @app_commands.command(
        name='games-help',
        description="List available games and their descriptions")
    async def games_help(self, interaction: discord.Interaction):
        """List available games and their descriptions"""
        embed = discord.Embed(
            title="🎮 Available Games",
            description="Explore the games you can play with Tux Bot!",
            color=discord.Color.blue())

        embed.add_field(
            name="/race",
            value="🏁 A text-based racing game. Type 'start' to race.",
            inline=False)
        embed.add_field(name="/trivia",
                        value="🧠 A Linux-themed trivia quiz.",
                        inline=False)
        embed.add_field(name="/guess",
                        value="🎲 A number guessing game.",
                        inline=False)
        embed.add_field(name="/hangman",
                        value="🔤 Play a word-guessing game.",
                        inline=False)
        embed.add_field(name="/rock-paper-scissors",
                        value="✊ Play Rock, Paper, Scissors.",
                        inline=False)
        embed.add_field(name="/wordsearch",
                        value="🔍 Solve a word search puzzle.",
                        inline=False)
        embed.add_field(name="/connect-four",
                        value="🔴 Play Connect Four against the bot.",
                        inline=False)
        embed.add_field(name="/math-quiz",
                        value="🧮 Answer math questions to test your skills.",
                        inline=False)
        embed.add_field(name="/tictactoe",
                        value="⭕ Play Tic Tac Toe with the bot.",
                        inline=False)
        embed.add_field(name="/snake",
                        value="🐍 Play a text-based Snake game.",
                        inline=False)

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(LinuxGames(bot))
