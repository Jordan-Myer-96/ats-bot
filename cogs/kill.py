# File: cogs/kill_revive_commands.py

import discord
from discord.ext import commands

class KillReviveCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_killed = False

    @commands.command(name='kill')
    @commands.check_any(commands.is_owner(), commands.has_role("Admin"))
    async def kill(self, ctx):
        if not self.is_killed:
            self.is_killed = True
            await ctx.send("Bot output has been stopped. Use `J$ can use revive` to resume.")
        else:
            await ctx.send("Bot is already stopped.")

    @commands.command(name='revive')
    @commands.is_owner()
    async def revive(self, ctx):
        if self.is_killed:
            self.is_killed = False
            await ctx.send("Bot output has been resumed.")
        else:
            await ctx.send("Bot is already active.")

    async def cog_check(self, ctx):
        return not self.is_killed

async def setup(bot):
    await bot.add_cog(KillReviveCommands(bot))