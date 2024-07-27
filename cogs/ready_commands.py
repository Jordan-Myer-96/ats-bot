import discord
from discord.ext import commands

class ReadyCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ready')
    async def ready(self, ctx, username: discord.Member = None):
        if username:
            if discord.utils.get(ctx.author.roles, name="Admin"):
                if discord.utils.get(username.roles, name="Student Athlete") or discord.utils.get(username.roles, name="Admin"):
                    self.bot.ready_users[username.id] = True
                    await ctx.send(f'{username.name} has been marked as ready by an admin.')
                else:
                    await ctx.send(f"{username.name} doesn't have the required role to be marked as ready.")
            else:
                await ctx.send("You don't have permission to mark others as ready.")
        else:
            if discord.utils.get(ctx.author.roles, name="Student Athlete") or discord.utils.get(ctx.author.roles, name="Admin"):
                self.bot.ready_users[ctx.author.id] = True
                await ctx.send(f'{ctx.author.name} is ready.')
            else:
                await ctx.send("You don't have permission to use this command.")
    @commands.command(name='whosready')
    async def whos_ready(self, ctx):
        ready_list = []
        not_ready_list = []
        
        for member in ctx.guild.members:
            if discord.utils.get(member.roles, name="Student Athlete") or discord.utils.get(member.roles, name="Admin"):
                if self.bot.ready_users.get(member.id, False):
                    ready_list.append(member.name)
                else:
                    not_ready_list.append(member.name)
        
        ready_message = "These users are all ready: " + ", ".join(ready_list) if ready_list else "No users are ready yet."
        not_ready_message = "These users are not ready: " + ", ".join(not_ready_list) if not_ready_list else "All users are ready!\nats"
        
        await ctx.send(f"{ready_message}\n{not_ready_message}")

    @commands.command(name='newweek')
    @commands.has_role("Admin")
    async def new_week(self, ctx):
        self.bot.ready_users.clear()  # Reset all ready statuses
        await ctx.send("A new week has started! All ready statuses have been reset.")

async def setup(bot):
    await bot.add_cog(ReadyCommands(bot))