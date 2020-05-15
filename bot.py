import discord
from discord.ext import commands
from discordToken import token
import scraper

import io
import aiohttp

client = commands.Bot(command_prefix = '.')

workshopMaps = scraper.getWorkshopMaps()

@client.event
async def on_ready():
    print('Bot is ready...')
    # workshopMaps = scraper.getWorkshopMaps()
    print(f'loaded up {len(workshopMaps)} maps')
    print(workshopMaps[0].name)
    print('Bot is ready...')

@client.event
async def on_member_join(member : discord.Member):
    channel = client.get_channel(708461726080827412)
    await channel.send(f'{member.mention} has joined the server!')

@client.event
async def on_member_remove(member : discord.Member):
    channel = client.get_channel(708461726080827412)
    await channel.send(f'{member.mention} has left the server...')

@client.command(brief = 'Returns current latency', description = 'Returns current latency')
async def ping(ctx):
    # await ctx.send(f'Pong! latency: {round(client.latency * 1000)}ms')
    embed = discord.Embed(title="Pong!", description='It took {}ms.'.format(round(client.latency * 1000)), color=0xffffff)
    await ctx.send(embed=embed)
    await ctx.send(f'Channel ID is {ctx.channel.id}')

@client.command(brief = 'Returns first map of the workshopMaps list', description = 'Returns first map of the workshopMaps list')
async def firstMap(ctx):
    map = workshopMaps[0]

    async with aiohttp.ClientSession() as session:
        async with session.get(map.imgLink) as resp:
            if resp.status != 200:
                return await ctx.send('Could not download file...')
            data = io.BytesIO(await resp.read())
            #await ctx.send(file=discord.File(data, 'cool_image.png'))

    embed = discord.Embed(title=map.name, description=f'\nMap Name: {map.name}\nAuthor: {map.author}\nDescription: {map.description}\nLink: {map.mapLink}', color=0xffffff)
    embed.set_image(url = map.imgLink)
    await ctx.send(embed=embed)
    

client.run(token)