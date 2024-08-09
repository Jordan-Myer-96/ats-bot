# File: print_messages.py

import asyncio
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

async def print_messages(server_id):
    await bot.wait_until_ready()
    server = bot.get_guild(int(server_id))
    if not server:
        print(f"Error: Server with ID {server_id} not found.")
        return

    channel = discord.utils.get(server.text_channels, name="admin-chat")
    if not channel:
        print(f"Error: #admin-chat channel not found in server {server.name}.")
        return

    messages = []
    async for message in channel.history(limit=50):
        timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
        content = message.content.replace('\n', ' ')  # Replace newlines with spaces
        messages.append(f"({timestamp}) {message.author.name}: {content}")

    messages.reverse()  # Reverse to get chronological order

    print(f"\n=== Last 50 messages from #admin-chat in {server.name} ===\n")
    for msg in messages:
        print(msg)
    print("\n=== End of messages ===\n")

    await bot.close()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    server_id = 1265765589641592924
    await print_messages(server_id)

def main():
    asyncio.run(bot.start(TOKEN))

if __name__ == "__main__":
    main()