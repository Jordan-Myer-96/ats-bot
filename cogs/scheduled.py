# File: cogs/scheduled_messages.py

import discord
from discord.ext import commands, tasks
from datetime import datetime, time
import pytz
import os
import asyncio

class ScheduledMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.time_file_path = os.path.join(self.base_path, 'scheduled_time.txt')
        self.est_time = self.load_scheduled_time()
        self.tag_not_ready.start()

    def cog_unload(self):
        self.tag_not_ready.cancel()

    def load_scheduled_time(self):
        try:
            with open(self.time_file_path, 'r') as f:
                hour, minute = map(int, f.read().strip().split(':'))
                return time(hour=hour, minute=minute)
        except FileNotFoundError:
            return time(hour=11, minute=0)  # Default to 11:00 AM EST if file doesn't exist
        except ValueError:
            print(f"Error reading {self.time_file_path}. Using default time.")
            return time(hour=11, minute=0)  # Default to 11:00 AM EST if there's an error

    def save_scheduled_time(self):
        with open(self.time_file_path, 'w') as f:
            f.write(f"{self.est_time.hour:02d}:{self.est_time.minute:02d}")

    def est_to_utc(self, est_time):
        est = pytz.timezone('US/Eastern')
        utc = pytz.UTC
        est_datetime = datetime.now(est).replace(hour=est_time.hour, minute=est_time.minute, second=0, microsecond=0)
        return est_datetime.astimezone(utc).time()

    @tasks.loop(time=time(hour=15, minute=0))  # Placeholder, will be updated in start_tasks
    async def tag_not_ready(self):
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
            await channel.send("Everyone is ready!")
        else:
            message = f"The following users are not ready: "
            mentions = [member.mention for member in not_ready_members]
            
            while mentions:
                current_message = message
                while mentions and len(current_message) + len(mentions[0]) + 2 <= 2000:
                    current_message += mentions.pop(0) + " "
                await channel.send(current_message)
                message = "Continued: "
                
            ready_channel = discord.utils.get(server.text_channels, name="ready-up")
            await channel.send(f"When ready, please ready up in {ready_channel.mention}")

    @tag_not_ready.before_loop
    async def before_tag_not_ready(self):
        await self.bot.wait_until_ready()
        self.tag_not_ready.change_interval(time=self.est_to_utc(self.est_time))
        print(f"Scheduled task set to run at {self.est_time.strftime('%I:%M %p')} EST")

    @commands.command(name='lastcall',help='Admin only: tag users in last-call who are not ready')
    @commands.check_any(commands.is_owner(), commands.has_role("Admin"))
    async def run_not_ready(self, ctx):
        await self.tag_not_ready()
        await ctx.send("Notification for not ready users has been sent.")

    @commands.command(name='setlastcalltime')
    @commands.check_any(commands.is_owner(), commands.has_role("Admin"))
    async def set_not_ready_time(self, ctx, hour: int, minute: int):
        if 0 <= hour < 24 and 0 <= minute < 60:
            old_time = self.est_time
            self.est_time = time(hour=hour, minute=minute)
            self.save_scheduled_time()
            
            # Wait for a short time to ensure file is updated
            await asyncio.sleep(3)
            
            # Read the time back from the file
            saved_time = self.load_scheduled_time()
            
            if saved_time != old_time:
                utc_time = self.est_to_utc(saved_time)
                self.tag_not_ready.change_interval(time=utc_time)
                await ctx.send(f"Notification time has been updated and set to {saved_time.strftime('%I:%M %p')} EST")
            else:
                await ctx.send(f"Notification time remains unchanged at {saved_time.strftime('%I:%M %p')} EST")
        else:
            await ctx.send("Invalid time. Please use 24-hour format (e.g., !setlastcalltime 11 0 for 11:00 AM)")

async def setup(bot):
    await bot.add_cog(ScheduledMessages(bot))