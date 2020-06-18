import discord
from discord.ext import commands
import platform
from datetime import date
from cogs import _scraper, _json
import asyncio

class Workshop(commands.Cog):
    
    def __init__(self, client):
        self.client = client

        # Load data from the JSON file
        self._data = _json.read_json('workshopMaps')

        self.workshopMaps = parseJSON(self._data)

        # Check how long it's been since an update,
        # if it's been more than a month then we'll update the data
        # and the JSON file
        self.lastUpdated = date.fromisoformat(self._data['lastUpdated'])
        today = date.today()
        timeDelta = today - self.lastUpdated        

        if (timeDelta.days > 30):
            print(f'It\'s been {timeDelta.days} since the last update, updating Workshop Maps....')
            self.workshopMaps = _scraper.getWorkshopMaps(self.workshopMaps)
            print('Update Complete. Saving new data...')
            self._data['workshopMaps'] = toDict(self.workshopMaps)
            self._data['lastUpdated'] = today.isoformat()
            _json.write_json(self._data, 'workshopMaps')
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
    async def getMap(self, ctx, *, name):        
        result = [ x for x in self.workshopMaps if name.lower() in x.nicknames]
        if (len(result) != 0):
            print(result[0])
            embed = getMapEmbed(result[0])
            await ctx.send(embed=embed)
        else:
            await ctx.send("I couldn't find that map, sorry!")

    def getMapByName(self, name):
        out = [ x for x in self.workshopMaps if name.lower() in x.nicknames]
        if out:
            return out[0]
        else:
            return []

    @commands.command()
    async def getMap2(self, ctx, *, name):
        map = self.getMapByName(name)
        if map:
            embed = getMapEmbed(map)
            await ctx.send(embed=embed)
        else:
            await ctx.send("I couldn't find that map, sorry!")

    @commands.command()
    async def addNickname(self, ctx, *, name):
        map = self.getMapByName(name)
        await ctx.send(f'So you want to add a nickname to the map \"{map.name}\" by {map.author}?')
        await ctx.send('Please confirm by reacting with 👍 or 👎')

        def check(reaction, user):
            return user == ctx.author

        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=30.0, check=check)

            await ctx.send(f'reaction: {reaction}')
            if str(reaction.emoji) == '👍':
                await ctx.send('Great! What Nickname would you like to add?')

                def check2(x):
                    return x.author == ctx.author
                
                try:
                    msg = await self.client.wait_for('message', check=check2, timeout=30)
                    # await ctx.send(f'lol you\'d like me to add {msg.content} wouldn\'t you')

                    nickname = msg.content
                    checkMaps = self.getMapByName(nickname)
                    if not checkMaps:
                        map.nicknames.append(nickname)

                        print('Map data updated, writing to JSON...')
                        self._data['workshopMaps'] = toDict(self.workshopMaps)
                        _json.write_json(self._data, 'workshopMaps')
                        print('...Update Complete!')

                        await ctx.send('OK! Nickname added!')
                        embed = getMapEmbed(map)
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send(f'Sorry! That nickname already belongs to \"{checkMaps.name}\" by {checkMaps.author}')
                except asyncio.TimeoutError:
                    await ctx.send('Looks like you didn\'t respond in time, pick a shorter nickname next time, ya dingus')
            else:
                await ctx.send('👎')
        except asyncio.TimeoutError:
            await ctx.send('👎')

    @commands.command()
    async def removeNickname(self, ctx, *, name):
        map = self.getMapByName(name)
        await ctx.send(f'Would you like to remove a nickname from  \"{map.name}\" by {map.author}?')
        await ctx.send('Please confirm by reacting with 👍 or 👎')

        try:
            await ctx.send(f'reaction: {reaction}')
            if str(reaction.emoji) == '👍':
                nickLength = len(map.nicknames)
                if nickLength != 1:
                    def checkUser(msg):
                        return msg.author == ctx.author

                    if nickLength == 2:
                        await ctx.send(f'Remove the nickname {map.nicknames[1]}?')
                        await ctx.send('Please confirm by reacting with 👍 or 👎')

                        #TODO: check and do shit

                    else:
                        message = 'Which nickname would you like to remove? \n'
                        choiceNum = 1
                        for name in map.nicknames[1:]:
                            message += f'{choiceNum} - {name}\n'
                            choiceNum++
                        await ctx.send(message)
                        response = await self.client.wait_for('message', check = checkUser, timeout = 20)
                        try:
                            responseInt = int(response.content)
                            if 
                else:
                    await ctx.send('It looks like that map has only one nickname so it can\'t be removed.')
            else:
                await ctx.send('👎')
        except asyncio.TimeoutError:
            await ctx.send('👎')

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