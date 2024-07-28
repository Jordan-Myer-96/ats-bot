import discord
from discord.ext import commands

class EchoCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='echo')
    @commands.has_role("Admin")
    async def echo(self, ctx, channel: discord.TextChannel = None, *, message: str):
        # If no channel is specified, default to #main-chat
        if channel is None:
            channel = discord.utils.get(ctx.guild.text_channels, name="main-chat")
            if channel is None:
                await ctx.send("Error: #main-chat channel not found and no other channel specified.")
                return
        
        # Check if the bot has permissions to send messages in the target channel
        if not channel.permissions_for(ctx.guild.me).send_messages:
            await ctx.send(f"Error: I don't have permission to send messages in {channel.mention}.")
            return

        # Send the message to the specified channel
        await channel.send(message)
        
        # Confirm to the user that the message was sent
        await ctx.send(f"Message echoed to {channel.mention}: {message}")

async def setup(bot):
    await bot.add_cog(EchoCommands(bot))