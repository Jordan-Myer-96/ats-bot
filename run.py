
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class MaddenLeagueBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        self.ready_users = {}
        self.command_responses = {}
        self.ignored_commands = ['twitch', 'me']

    async def setup_hook(self):
        # Load cogs
        # await self.load_extension('cogs.msg')
        # logging.info(f'Loaded msg cog')
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
                logging.info(f'Loaded cog: {filename[:-3]}')
        self.allowed_mentions = discord.AllowedMentions(everyone=True, users=True, roles=True)

    async def on_ready(self):
        logging.info(f'{self.user} has connected to Discord!')

    async def on_message(self, message):
        if message.author.bot:
            return

        # Check if the message starts with the command prefix and is an ignored command
        if message.content.startswith(self.command_prefix):
            command = message.content[len(self.command_prefix):].split()[0]
            if command in self.ignored_commands:
                return  # Ignore the command

        await self.process_commands(message)

    async def on_message_delete(self, message):
        if message.id in self.command_responses:
            response_message = self.command_responses[message.id]
            await response_message.delete()
            del self.command_responses[message.id]

    async def process_commands(self, message):
        if message.author.bot:
            return

        ctx = await self.get_context(message)
        if ctx.valid:
            # Check if the bot is in "killed" state
            kill_revive_cog = self.get_cog('kill')
            if kill_revive_cog and kill_revive_cog.is_killed:
                if not (ctx.command and ctx.command.name == 'revive'):
                    await ctx.send('Bot is under maintenance')
                    return  # Don't process commands if bot is killed, except for 'revive'

            try:
                await self.invoke(ctx)
            except commands.CommandError as e:
                await ctx.send(f'An error occurred: {str(e)}')
            except Exception as e:
                await ctx.send('An unexpected error occurred. Please try again later.')
                # You might want to log this error for debugging
                print(f'Unexpected error: {str(e)}')

bot = MaddenLeagueBot()

@bot.command(name='reload')
@commands.is_owner()
async def reload(ctx, extension):
    try:
        await bot.reload_extension(f'cogs.{extension}')
        await ctx.send(f'{extension} has been reloaded.')
    except commands.ExtensionError as e:
        await ctx.send(f'{e.__class__.__name__}: {e}')

# Get the bot token from environment variables
bot_token = os.getenv('DISCORD_BOT_TOKEN')
if bot_token is None:
    raise ValueError("No bot token found in environment variables. Make sure to set DISCORD_BOT_TOKEN in your .env file.")

if __name__ == "__main__":
    bot.run(bot_token)