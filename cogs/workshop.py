import discord
from discord.ext import commands
import platform
from datetime import date
from cogs import _scraper, _json

class Workshop(commands.Cog):
    
    def __init__(self, client):
        self.client = client

        # Load data from the JSON file
        data = _json.read_json('workshopMaps')

        self.workshopMaps = parseJSON(data)

        # Check how long it's been since an update,
        # if it's been more than a month then we'll update the data
        # and the JSON file
        self.lastUpdated = date.fromisoformat(data['lastUpdated'])
        today = date.today()
        timeDelta = today - self.lastUpdated        

        if (timeDelta.days > 30):
            print(f'It\'s been {timeDelta.days} since the last update, updating Workshop Maps....')
            self.workshopMaps = _scraper.getWorkshopMaps(self.workshopMaps)
            print('Update Complete. Saving new data...')
            data['workshopMaps'] = toDict(self.workshopMaps)
            data['lastUpdated'] = today.isoformat()
            _json.write_json(data, 'workshopMaps')
            print('Save complete.')
        else:
            print(f'Only {timeDelta.days} days since last update, no need to update...')

        print(f'loaded up {len(self.workshopMaps)} maps')


    @commands.Cog.listener()
    async def on_ready(self):
        print("Workshop Cog has been loaded...")

    # Commands

    @commands.command()
    async def getMapByIndex(self, ctx, index):
        embed = getMapEmbed(self.workshopMaps[int(index)])
        await ctx.send(embed = embed)

    @commands.command()
    async def getMapByName(self, ctx, *, name):        
        result = [ x for x in self.workshopMaps if name.lower() in x.nicknames]
        if (len(result) != 0):
            embed = getMapEmbed(result[0])
            await ctx.send(embed=embed)
        else:
            await ctx.send("I couldn't find that map, sorry!")

# Functions

def getMapEmbed(map : _scraper.WorkshopMap):
    embed = discord.Embed(title = map.name)
    embed.set_thumbnail(url = map.imgLink)
    embed.add_field(name = 'Author', value = map.author, inline = False)
    embed.add_field(name = 'Description', value = map.description, inline = False)
    embed.add_field(name = 'Steam Link', value = f'steam://openurl/{map.mapLink}', inline = False)
    
    nicknameStr = ''
    for x in range(len(map.nicknames)):
        nicknameStr += map.nicknames[x]
        if x != (len(map.nicknames) - 1):
            nicknameStr += ', '
    
    embed.add_field(name = 'Nicknames', value = nicknameStr, inline = False)

    return embed

def parseJSON(data):
    maps = []
    for map in data['workshopMaps']:
        out = _scraper.WorkshopMap()
        for key, value in map.items():
          setattr(out, key, value)   

        maps.append(out)
    return maps

def toDict(maps):
    outArray = []

    for map in maps:
        d = map.__dict__
        outArray.append(d)
    return outArray

def setup(client):
    client.add_cog(Workshop(client))