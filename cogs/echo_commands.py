import discord
from discord.ext import commands

class EchoCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='echo')
    @commands.has_role("Admin")
    async def echo(self, ctx, *, message: str):
        # Find the #main-chat channel
        main_chat = discord.utils.get(ctx.guild.text_channels, name="main-chat")
        
        if main_chat is None:
            await ctx.send("Error: #main-chat channel not found.")
            return

        # Send the message to #main-chat
        await main_chat.send(message)
        
        # Confirm to the user that the message was sent
        await ctx.send(f"Message echoed to #main-chat: {message}")

async def setup(bot):
    await bot.add_cog(EchoCommands(bot))