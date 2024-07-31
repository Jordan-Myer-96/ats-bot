# File: cogs/scheduled_messages_test.py

import discord
from discord.ext import commands, tasks
from datetime import datetime, time
import pytz

class ScheduledMessagesTest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.est_time = time(hour=19, minute=3)  # Default to 7:00 AM EST
        self.tag_not_ready_test.start()

    def cog_unload(self):
        self.tag_not_ready_test.cancel()

    def est_to_utc(self, est_time):
        est = pytz.timezone('US/Eastern')
        utc = pytz.UTC
        # Use today's date with EST time
        est_datetime = datetime.now(est).replace(hour=est_time.hour, minute=est_time.minute, second=0, microsecond=0)
        return est_datetime.astimezone(utc).time()

    @tasks.loop(time=time(hour=11, minute=0))  # Placeholder, will be updated in start_tasks
    async def tag_not_ready_test(self):
        server_id = 1265765589641592924  # Replace with your specific server ID
        channel_name = "last-call"  # Channel name to send the message

        server = self.bot.get_guild(server_id)
        if not server:
            print(f"Server with ID {server_id} not found.")
            return

        channel = discord.utils.get(server.text_channels, name=channel_name)
        if not channel:
            print(f"Channel '{channel_name}' not found in server {server.name}.")
            return

        ready_cog = self.bot.get_cog('ReadyCommands')
        if not ready_cog:
            print("ReadyCommands cog not found.")
            return

        not_ready_members = [member for member in server.members 
                             if (discord.utils.get(member.roles, name="Student Athlete") or 
                                 discord.utils.get(member.roles, name="Admin")) and 
                             str(member.id) not in ready_cog.ready_users]
        
        if not not_ready_members:
            await channel.send("[TEST] Everyone is ready!")
        else:
            message = f"[TEST] The following users would have been tagged as not ready at {self.est_time.strftime('%I:%M %p')} EST: "
            usernames = [member.name for member in not_ready_members]
            
            while usernames:
                current_message = message
                while usernames and len(current_message) + len(usernames[0]) + 2 <= 2000:
                    current_message += usernames.pop(0) + ", "
                current_message = current_message.rstrip(", ")  # Remove trailing comma and space
                await channel.send(current_message)
                message = "[TEST] Continued: "

    @tag_not_ready_test.before_loop
    async def before_tag_not_ready_test(self):
        await self.bot.wait_until_ready()
        self.tag_not_ready_test.change_interval(time=self.est_to_utc(self.est_time))
        print(f"Scheduled task set to run at {self.est_time.strftime('%I:%M %p')} EST")

    @commands.command(name='runtestnotready')
    @commands.has_permissions(manage_messages=True)
    async def run_test_not_ready(self, ctx):
        await self.tag_not_ready_test()
        await ctx.send("Test notification for not ready users has been sent.")

    @commands.command(name='setnotreadytime')
    @commands.has_permissions(manage_messages=True)
    async def set_not_ready_time(self, ctx, hour: int, minute: int):
        if 0 <= hour < 24 and 0 <= minute < 60:
            self.est_time = time(hour=hour, minute=minute)
            utc_time = self.est_to_utc(self.est_time)
            self.tag_not_ready_test.change_interval(time=utc_time)
            await ctx.send(f"Notification time set to {self.est_time.strftime('%I:%M %p')} EST")
        else:
            await ctx.send("Invalid time. Please use 24-hour format (e.g., !setnotreadytime 7 0 for 7:00 AM)")

async def setup(bot):
    await bot.add_cog(ScheduledMessagesTest(bot))