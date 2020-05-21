import discord
from discord.ext import commands
from discordToken import token
import cogs._scraper
import platform # For stats
import json
from pathlib import Path
import os

cwd = Path(__file__).parents[0]
cwd = str(cwd)

# workshopMaps = cogs._scraper.getWorkshopMaps()

prefixes = ['.', '!', '?', 'test.', 'hey you, ', 'hey bot, ']

client = commands.Bot(command_prefix = prefixes, case_insensitive = True)
client.version = '0.0.2'
client.blacklisted_users = []

@client.event
async def on_ready():
    await client.change_presence(activity = discord.Game('python is cool'))
    load_cogs()
    print('Bot is ready...')


@client.event
async def on_message(message):
    # Ignore ourselves
    if message.author.id == client.user.id:
        return

    # Blacklist system
    if message.author.id in client.blacklisted_users:
        return

    #Whenever the bot is tagged, respond with its prefix
    if f"<@!{client.user.id}>" in message.content:
        prefixString =""
        for i in range(0, (len(prefixes) - 2)):
            prefixString += f'"{prefixes[i]}", '
        prefixString += f'and "{prefixes[len(prefixes) - 1]}"'
        prefixMsg = await message.channel.send(f"My prefixes here are {prefixString}")
        await prefixMsg.add_reaction('👀')

    await client.process_commands(message)

@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'The {extension} Cog has been loaded!')

@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    await ctx.send(f'The {extension} Cog has been unloaded!')

@client.command()
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'The {extension} Cog has been reloaded!')

def load_cogs():
    for file in os.listdir("./cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            client.load_extension(f"cogs.{file[:-3]}")

client.run(token)