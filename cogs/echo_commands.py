# File: cogs/echo_commands.py

import discord
from discord.ext import commands
import re

class EchoCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='echo')
    @commands.has_permissions(manage_messages=True)
    async def echo(self, ctx, *, content: str):
        # Try to extract channel and message
        channel_match = re.match(r'(<#\d+>|\S+)\s+(.*)', content, re.DOTALL)
        
        if channel_match:
            channel_input, message = channel_match.groups()
            # Try to get channel by mention or name
            channel = await self.get_channel(ctx, channel_input)
        else:
            channel = discord.utils.get(ctx.guild.text_channels, name="main-chat")
            message = content

        if channel is None:
            await ctx.send("Error: Couldn't find the specified channel. Using #main-chat.")
            channel = discord.utils.get(ctx.guild.text_channels, name="main-chat")
            if channel is None:
                await ctx.send("Error: #main-chat channel not found. Please specify a valid channel.")
                return

        # Check permissions
        if not channel.permissions_for(ctx.guild.me).send_messages:
            await ctx.send(f"Error: I don't have permission to send messages in {channel.mention}.")
            return

        # Parse and replace user mentions
        message = await self.parse_mentions(ctx, message)

        # Send the message
        sent_message = await channel.send(message)
        await ctx.send(f"Message echoed to {channel.mention}: {message}")

        # Process the message if it's a command
        if message.startswith(self.bot.command_prefix):
            # Create a new context for the command
            new_ctx = await self.bot.get_context(sent_message)
            if new_ctx.valid:
                await self.bot.invoke(new_ctx)

    async def get_channel(self, ctx, channel_input):
        # Check if it's a channel mention
        if channel_input.startswith('<#') and channel_input.endswith('>'):
            channel_id = int(channel_input[2:-1])
            return ctx.guild.get_channel(channel_id)
        
        # Check if it's a channel name (with or without #)
        channel_name = channel_input.lstrip('#')
        return discord.utils.get(ctx.guild.text_channels, name=channel_name)

    async def parse_mentions(self, ctx, message):
        # Regular expression to find user mentions or names
        mention_pattern = re.compile(r'<@!?(\d+)>|@(\w+)')

        def replace_mention(match):
            if match.group(1):  # It's a mention with ID
                user_id = int(match.group(1))
                user = ctx.guild.get_member(user_id)
                return f'<@{user_id}>' if user else match.group(0)
            else:  # It's a username
                username = match.group(2)
                user = discord.utils.get(ctx.guild.members, name=username)
                return f'<@{user.id}>' if user else f'@{username}'

        return mention_pattern.sub(replace_mention, message)

async def setup(bot):
    await bot.add_cog(EchoCommands(bot))