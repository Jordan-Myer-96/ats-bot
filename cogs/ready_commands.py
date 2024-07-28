import discord
from discord.ext import commands

class ReadyCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, 'ready_users'):
            bot.ready_users = set()

    @commands.command(name='ready')
    async def ready(self, ctx, *users: discord.Member):
        if not users:
            users = [ctx.author]

        valid_users = []
        invalid_users = []

        for user in users:
            if discord.utils.get(user.roles, name="Admin") or discord.utils.get(user.roles, name="Student Athlete"):
                self.bot.ready_users.add(user.id)
                valid_users.append(user.name)
            else:
                invalid_users.append(user.name)

        response = []
        if valid_users:
            response.append(f"The following users are now ready: {', '.join(valid_users)}")
        if invalid_users:
            response.append(f"The following users don't have the required role: {', '.join(invalid_users)}")

        await ctx.send("\n".join(response) or "No valid users were marked as ready.")

    @commands.command(name='whosready')
    async def whos_ready(self, ctx):
        ready_members = [member.name for member in ctx.guild.members if member.id in self.bot.ready_users]
        not_ready_members = [member.name for member in ctx.guild.members 
                             if (discord.utils.get(member.roles, name="Student Athlete") or 
                                 discord.utils.get(member.roles, name="Admin")) and 
                             member.id not in self.bot.ready_users]
        
        ready_message = "These users are all ready: " + ", ".join(ready_members) if ready_members else "No users are ready yet."
        not_ready_message = "These users are not ready: " + ", ".join(not_ready_members) if not_ready_members else "All users are ready!"
        
        await ctx.send(f"{ready_message}\n{not_ready_message}")

    @commands.command(name='newweek')
    @commands.has_role("Admin")
    async def new_week(self, ctx):
        self.bot.ready_users.clear()
        await ctx.send("A new week has started! All ready statuses have been reset.")

async def setup(bot):
    await bot.add_cog(ReadyCommands(bot))