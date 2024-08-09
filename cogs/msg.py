import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone
import asyncio

class MessageLogger(commands.Cog):
    def __init__(self, bot, server_id, channel_name="admin-chat"):
        self.bot = bot
        self.server_id = server_id
        self.channel_name = channel_name
        self.log_file = "S20_admin_chat_log.txt"
        # Ensure last_logged_time is UTC-aware
        self.last_logged_time = datetime.now(timezone.utc) - timedelta(seconds=10)
        self.bot.loop.create_task(self.log_messages_periodically())

    async def log_messages_periodically(self):
        await self.bot.wait_until_ready()
        print("Bot is ready and will log messages every 5 minuites.")
        while not self.bot.is_closed():
            await self.log_new_messages()
            await asyncio.sleep(10)  # Run every 10 seconds

    async def log_new_messages(self):
        print(f"Checking for new messages since {self.last_logged_time} (UTC)")
        server = self.bot.get_guild(self.server_id)
        if not server:
            print(f"Error: Server with ID {self.server_id} not found.")
            return

        channel = discord.utils.get(server.channels, name=self.channel_name)
        if not channel:
            print(f"Error: #{self.channel_name} channel not found in the specified server.")
            return

        new_messages = []
        async for message in channel.history(limit=None, after=self.last_logged_time):
            timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            content = message.content.replace('\n', ' ')  # Replace newlines with spaces
            log_entry = f"({timestamp}) {message.author.name}: {content}\n"
            new_messages.append((message, log_entry))

        if new_messages:
            new_messages.reverse()  # To maintain chronological order
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(''.join(entry for _, entry in new_messages))
            
            # Update last_logged_time to the last message's timestamp
            self.last_logged_time = new_messages[-1][0].created_at.replace(tzinfo=timezone.utc)
            print(f"Logged {len(new_messages)} new messages. Last logged time updated to {self.last_logged_time}.")
        else:
            print("No new messages to log.")

async def setup(bot):
    server_id = 1265765589641592924  # Replace with your desired server ID
    await bot.add_cog(MessageLogger(bot, server_id))
