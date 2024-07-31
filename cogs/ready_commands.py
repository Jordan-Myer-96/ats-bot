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

    @commands.command(name='ready', help='Mark yourself or specified users as ready')
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

    @commands.command(name='unready', help='Remove ready status from yourself or specified users (admin only for others)')
    async def remove_ready(self, ctx, *users):
        is_admin = discord.utils.get(ctx.author.roles, name="Admin") or ctx.author.guild_permissions.administrator

        if not users:
            users = [ctx.author.name]
        elif not is_admin and len(users) > 1 or (not is_admin and (len(users) == 1 and users[0].lower() != ctx.author.name.lower())):
            await ctx.send("You can only remove your own ready status. Admins can remove status for other users.")
            return

        removed_users = []
        not_ready_users = []
        invalid_users = []

        for user in users:
            member = discord.utils.get(ctx.guild.members, name=user)
            if member is None:
                invalid_users.append(user)
            elif str(member.id) in self.ready_users:
                del self.ready_users[str(member.id)]
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

    @commands.command(name='whosready', aliases=['whoisready'], help='List users who are ready and not ready')
    async def whos_ready(self, ctx):
        ready_members = [member.name for member in ctx.guild.members if str(member.id) in self.ready_users]
        not_ready_members = [member.name for member in ctx.guild.members 
                             if (discord.utils.get(member.roles, name="Student Athlete") or 
                                 discord.utils.get(member.roles, name="Admin")) and 
                             str(member.id) not in self.ready_users]
        
        ready_message = "These users are all ready: " + ", ".join(ready_members) if ready_members else "No users are ready yet."
        not_ready_message = "These users are not ready: " + ", ".join(not_ready_members) if not_ready_members else "All users are ready!"
        
        await ctx.send(f"{ready_message}\n{not_ready_message}")

    @commands.command(name='newweek', help='Reset all ready statuses for a new week')
    @commands.has_role("Admin")
    async def new_week(self, ctx):
        self.ready_users.clear()
        self.save_ready_users()
        await ctx.send("A new week has started! All ready statuses have been reset.")

    @commands.command(name='commands', help='List all available commands with descriptions')
    async def list_commands(self, ctx):
        command_list = [f"`{command.name}`: {command.help}" for command in self.bot.commands if command.help]
        if command_list:
            commands_str = "\n".join(command_list)
            embed = discord.Embed(title="Available Commands", description=commands_str, color=discord.Color.blue())
        else:
            embed = discord.Embed(title="Available Commands", description="No commands with descriptions available.", color=discord.Color.blue())
        
        await ctx.send(embed=embed)

    @commands.command(name='users', help='List all usernames for easy copy-paste')
    async def list_users(self, ctx):
        try:
            usernames = [member.name for member in ctx.guild.members if not member.bot]
            if not usernames:
                await ctx.send("No users found. This might be due to member intents not being enabled.")
                return

            usernames.sort()  # Sort alphabetically
            users_str = " ".join(usernames)

            if len(users_str) > 2000:
                # If the message is too long, split it into multiple messages
                chunks = [users_str[i:i+1900] for i in range(0, len(users_str), 1900)]
                for i, chunk in enumerate(chunks, 1):
                    await ctx.send(f"```Users (Part {i}/{len(chunks)}):\n{chunk}```")
            else:
                await ctx.send(f"```Users:\n{users_str}```")

        except discord.Forbidden:
            await ctx.send("I don't have permission to perform this action.")
        except discord.HTTPException as e:
            await ctx.send(f"An HTTP error occurred: {str(e)}")
        except Exception as e:
            await ctx.send(f"An error occurred while processing the command: {str(e)}")

async def setup(bot):
    await bot.add_cog(ReadyCommands(bot))