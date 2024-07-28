# File: cogs/ready_commands.py

import discord
from discord.ext import commands
import json
import os

class ReadyCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ready_users_file = 'ready_users.json'
        self.ready_users = self.load_ready_users()

    def load_ready_users(self):
        if os.path.exists(self.ready_users_file):
            try:
                with open(self.ready_users_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Error reading {self.ready_users_file}. Starting with empty ready users.")
        return {}

    def save_ready_users(self):
        with open(self.ready_users_file, 'w') as f:
            json.dump(self.ready_users, f)

    @commands.command(name='ready')
    async def ready(self, ctx, *users):
        if not users:
            users = [ctx.author.name]

        valid_users = []
        invalid_users = []
        no_permission_users = []

        for user in users:
            member = discord.utils.get(ctx.guild.members, name=user)
            if member is None:
                invalid_users.append(user)
            elif discord.utils.get(member.roles, name="Admin") or discord.utils.get(member.roles, name="Student Athlete"):
                self.ready_users[str(member.id)] = True
                valid_users.append(member.name)
            else:
                no_permission_users.append(member.name)

        self.save_ready_users()

        response = []
        if valid_users:
            response.append(f"The following users are now ready: {', '.join(valid_users)}")
        if invalid_users:
            if len(invalid_users) == 1:
                response.append(f"Invalid username: {invalid_users[0]}")
            else:
                response.append(f"The following usernames are invalid: {', '.join(invalid_users)}")
        if no_permission_users:
            response.append(f"The following users don't have the required role: {', '.join(no_permission_users)}")

        await ctx.send("\n".join(response) or "No valid users were marked as ready.")

    @commands.command(name='removeready')
    async def remove_ready(self, ctx, *users):
        if not (discord.utils.get(ctx.author.roles, name="Admin") or ctx.author.guild_permissions.manage_messages):
            await ctx.send("You need to have the Admin role or Manage Messages permission to use this command.")
            return

        if not users:
            await ctx.send("Please specify at least one user to remove ready status from.")
            return

        removed_users = []
        not_ready_users = []
        invalid_users = []

        for user in users:
            member = discord.utils.get(ctx.guild.members, name=user)
            if member is None:
                invalid_users.append(user)
            elif self.ready_users.pop(str(member.id), None) is not None:
                removed_users.append(member.name)
            else:
                not_ready_users.append(member.name)

        self.save_ready_users()

        response = []
        if removed_users:
            response.append(f"Removed ready status from: {', '.join(removed_users)}")
        if not_ready_users:
            response.append(f"The following users were not marked as ready: {', '.join(not_ready_users)}")
        if invalid_users:
            if len(invalid_users) == 1:
                response.append(f"Invalid username: {invalid_users[0]}")
            else:
                response.append(f"The following usernames are invalid: {', '.join(invalid_users)}")

        await ctx.send("\n".join(response) or "No changes were made to ready statuses.")

    @commands.command(name='whosready')
    async def whos_ready(self, ctx):
        ready_members = [member.name for member in ctx.guild.members if str(member.id) in self.ready_users]
        not_ready_members = [member.name for member in ctx.guild.members 
                             if (discord.utils.get(member.roles, name="Student Athlete") or 
                                 discord.utils.get(member.roles, name="Admin")) and 
                             str(member.id) not in self.ready_users]
        
        ready_message = "These users are all ready: " + ", ".join(ready_members) if ready_members else "No users are ready yet."
        not_ready_message = "These users are not ready: " + ", ".join(not_ready_members) if not_ready_members else "All users are ready!"
        
        await ctx.send(f"{ready_message}\n{not_ready_message}")

    @commands.command(name='newweek')
    @commands.has_role("Admin")
    async def new_week(self, ctx):
        self.ready_users.clear()
        self.save_ready_users()
        await ctx.send("A new week has started! All ready statuses have been reset.")

async def setup(bot):
    await bot.add_cog(ReadyCommands(bot))