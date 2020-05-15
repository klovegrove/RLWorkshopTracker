import discord
from discord.ext import commands
from discordToken import token

tokenOld = 'NzA4NDUzMjI0OTg5OTgyNzMx.Xr4l3w.dJEp0N0DBqqTUoEuQYWpShsKc5I'
client = commands.Bot(command_prefix = '.')

@client.event
async def on_ready():
    print('Bot is ready...')

@client.event
async def on_member_join(member : discord.Member):
    channel = client.get_channel(708461726080827412)
    await channel.send(f'{member.mention} has joined the server!')

@client.event
async def on_member_remove(member : discord.Member):
    channel = client.get_channel(708461726080827412)
    await channel.send(f'{member.mention} has left the server...')

@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! latency: {round(client.latency * 1000)}ms')
    await ctx.send(f'Channel ID is {ctx.channel.id}')

client.run(token)