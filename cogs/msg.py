# File: cogs/message_logger.py

import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio

class MessageLogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_file = "main_chat_log.txt"
        self.last_logged_time = datetime.utcnow()
        self.bot.loop.create_task(self.log_messages_periodically())

    async def log_messages_periodically(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            await self.log_new_messages()
            await asyncio.sleep(30)  # Run every 30 seconds

    async def log_new_messages(self):
        channel = discord.utils.get(self.bot.get_all_channels(), name="main-chat")
        if not channel:
            print("Error: #main-chat channel not found.")
            return

        new_messages = []
        async for message in channel.history(limit=None, after=self.last_logged_time):
            timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            content = message.content.replace('\n', ' ')  # Replace newlines with spaces
            log_entry = f"({timestamp}) {message.author.name}: {content}"
            new_messages.append(log_entry)

        if new_messages:
            new_messages.reverse()  # To maintain chronological order
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write('\n' + '\n'.join(new_messages))
            
            self.last_logged_time = datetime.utcnow()
            print(f"Logged {len(new_messages)} new messages.")

async def setup(bot):
    await bot.add_cog(MessageLogger(bot))