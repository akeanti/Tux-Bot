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

    @app_commands.command(name='connect-four',
                          description="Play Connect Four against the bot")
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
            f"🟡 Connect Four! {interaction.user.mention} goes first.")
        while not winner and not is_full():
            await interaction.followup.send(print_board())
            await interaction.followup.send("Choose a column (0-6):")
            msg = await self.wait_for_message(interaction)
            if msg:
                try:
                    col = int(msg.content)
                    if col < 0 or col >= 7 or board[0][col] != '⚪':
                        await interaction.followup.send(
                            "❌ Invalid column. Please choose another.")
                        continue

                    drop_piece(col, player)
                    if check_winner() == player:
                        winner = player
                        break

                    if is_full():
                        break

                    # Bot's turn
                    bot_col = random.choice(
                        [c for c in range(7) if board[0][c] == '⚪'])
                    drop_piece(bot_col, bot)
                    if check_winner() == bot:
                        winner = bot
                        break

                except ValueError:
                    await interaction.followup.send(
                        '🚫 Please enter a valid number.')

        await interaction.followup.send(print_board())
        if winner:
            await interaction.followup.send(
                f'🎉 {interaction.user.mention} wins!' if winner ==
                player else '🤖 Bot wins!')
        else:
            await interaction.followup.send('🔄 It\'s a tie!')

    @app_commands.command(
        name='math-quiz',
        description="Test your math skills with a quick quiz")
    async def math_quiz(self, interaction: discord.Interaction):
        """Test your math skills with a quick quiz"""
        operations = {
            "addition": lambda x, y: x + y,
            "subtraction": lambda x, y: x - y,
            "multiplication": lambda x, y: x * y,
            "division": lambda x, y: x / y
        }
        op = random.choice(list(operations.keys()))
        num1, num2 = random.randint(1, 10), random.randint(1, 10)
        correct_answer = operations[op](num1, num2)

        await interaction.response.send_message(
            f"🔢 What is {num1} {op} {num2}?")

        msg = await self.wait_for_message(interaction)
        if msg:
            try:
                user_answer = float(msg.content)
                if user_answer == correct_answer:
                    await interaction.followup.send('✅ Correct!')
                else:
                    await interaction.followup.send(
                        f'❌ Wrong answer. The correct answer was {correct_answer}'
                    )
            except ValueError:
                await interaction.followup.send(
                    '🚫 Please enter a valid number.')

    @app_commands.command(name='tictactoe',
                          description="Play Tic-Tac-Toe with the bot")
    async def tictactoe(self, interaction: discord.Interaction):
        """Play Tic-Tac-Toe with the bot"""
        board = [' ' for _ in range(9)]
        player, bot = 'X', 'O'
        winner = None

        def print_board():
            return f"""
            {board[0]} | {board[1]} | {board[2]}
            ---------
            {board[3]} | {board[4]} | {board[5]}
            ---------
            {board[6]} | {board[7]} | {board[8]}
            """

        def check_winner():
            lines = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7),
                     (2, 5, 8), (0, 4, 8), (2, 4, 6)]
            for a, b, c in lines:
                if board[a] == board[b] == board[c] and board[a] != ' ':
                    return board[a]
            return None

        def is_full():
            return all(cell != ' ' for cell in board)

        await interaction.response.send_message(
            f"✖️ Tic-Tac-Toe! {interaction.user.mention} goes first.")
        while not winner and not is_full():
            await interaction.followup.send(print_board())
            await interaction.followup.send("Choose a position (1-9):")
            msg = await self.wait_for_message(interaction)
            if msg:
                try:
                    pos = int(msg.content) - 1
                    if pos < 0 or pos >= 9 or board[pos] != ' ':
                        await interaction.followup.send(
                            "❌ Invalid position. Please choose another.")
                        continue

                    board[pos] = player
                    if check_winner() == player:
                        winner = player
                        break

                    if is_full():
                        break

                    # Bot's turn
                    bot_pos = random.choice(
                        [i for i in range(9) if board[i] == ' '])
                    board[bot_pos] = bot
                    if check_winner() == bot:
                        winner = bot
                        break

                except ValueError:
                    await interaction.followup.send(
                        '🚫 Please enter a valid number.')

        await interaction.followup.send(print_board())
        if winner:
            await interaction.followup.send(
                f'🎉 {interaction.user.mention} wins!' if winner ==
                player else '🤖 Bot wins!')
        else:
            await interaction.followup.send('🔄 It\'s a tie!')

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
