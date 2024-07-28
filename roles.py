import discord
import os
from dotenv import load_dotenv
from discord.ext import commands

# Load environment variables
load_dotenv()

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def print_roles(ctx):
    roles = ctx.guild.roles
    for role in roles:
        print(f"{role.id}")

# Get the bot token from environment variables
bot_token = os.getenv('DISCORD_BOT_TOKEN')
if bot_token is None:
    raise ValueError("No bot token found in environment variables. Make sure to set DISCORD_BOT_TOKEN in your .env file.")

if __name__ == "__main__":
    bot.run(bot_token)