import discord
from discord.ext import commands
import platform
from cogs import _scraper, _json

class Workshop(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        self.workshopMaps = _scraper.getWorkshopMaps()
        print(f'loaded up {len(self.workshopMaps)} maps')


    @commands.Cog.listener()
    async def on_ready(self):
        print("Workshop Cog has been loaded...")

    # Commands

    @commands.command()
    async def getMapByIndex(self, ctx, index):
        embed = getMapEmbed(self.workshopMaps[int(index)])
        await ctx.send(embed = embed)

def getMapEmbed(map : _scraper.WorkshopMap):
    embed = discord.Embed(title = map.name)
    embed.set_thumbnail(url = map.imgLink)
    embed.add_field(name = 'Author', value = map.author, inline = False)
    embed.add_field(name = 'Description', value = map.description, inline = False)
    embed.add_field(name = 'Steam Link', value = f'steam://openurl/{map.mapLink}', inline = False)

    return embed

def setup(client):
    client.add_cog(Workshop(client))