import discord
from discord.ext import commands
import platform
from datetime import date
from cogs import _scraper, _json
import asyncio

# TODO: - add method for looking up newly added maps
#           *gonna have to start storing the date the map is added
#       - add more error handling, like for map lookups
#       - add tracking data
#       - tracking lookup
#       - leaderboards
#       - VALIDATION FOR TRACKING MEASURES


class Workshop(commands.Cog):
    def __init__(self, client):
        self.client = client

        # Load data from the JSON file
        self._data = _json.read_json("workshopMaps")

        self.workshopMaps = parseJSON(self._data)

        # Check how long it's been since an update,
        # if it's been more than a month then we'll update the data
        # and the JSON file

        # I SHOULD MAKE A BACKGROUND TASK FOR THIS
        self.lastUpdated = date.fromisoformat(self._data["lastUpdated"])
        today = date.today()
        timeDelta = today - self.lastUpdated

        if timeDelta.days > 30:
            print(
                f"It's been {timeDelta.days} since the last update, updating Workshop Maps...."
            )
            self.workshopMaps = _scraper.getWorkshopMaps(self.workshopMaps)
            print("Update Complete. Saving new data...")
            self._data["workshopMaps"] = toDict(self.workshopMaps)
            self._data["lastUpdated"] = today.isoformat()
            _json.write_json(self._data, "workshopMaps")
            print("Save complete.")
        else:
            print(f"Only {timeDelta.days} days since last update, no need to update...")

        print(f"loaded up {len(self.workshopMaps)} maps")

    ## Class Functions

    async def checkTest(self, ctx, intro, negative=None, reacts=None):
        await ctx.send(intro)
        try:
            if reacts is not None:
                msg = await ctx.send("Please confirm by reacting with 👍 or 👎")
                for emoji in reacts:
                    await msg.add_reaction(emoji)

                def check(reaction, user):
                    return user == ctx.author and (
                        str(reaction.emoji) == "👍" or str(reaction.emoji) == "👎"
                    )

                reaction, user = await self.client.wait_for(
                    "reaction_add", timeout=10.0, check=check
                )
                reactEmoji = str(reaction.emoji)

                if reactEmoji == "👍":
                    return True
                elif negative is not None:
                    await ctx.send(negative)
                    return False
            else:

                def check(message):
                    return ctx.author == message.author

                message = await self.client.wait_for(
                    "message", timeout=30.0, check=check
                )
                return message
        except asyncio.TimeoutError:
            await ctx.send("Looks like you didn't respond in time... Whoops!") 

    def getMapByName(self, name):
        return next((x for x in self.workshopMaps if name.lower() in x.nicknames), None)

    def jsonUpdate(self):
        print("Map data updated, writing to JSON...")
        self._data["workshopMaps"] = toDict(self.workshopMaps)
        _json.write_json(self._data, "workshopMaps")
        print("...Update Complete!")

    ## Listeners

    @commands.Cog.listener()
    async def on_ready(self):
        print("Workshop Cog has been loaded...")

    ## Commands

    @commands.command()
    async def getMapByIndex(self, ctx, index):
        embed = getMapEmbed(self.workshopMaps[int(index)])
        await ctx.send(embed=embed)

    @commands.command()
    async def getMap(self, ctx, *, name):
        """
        Returns the map with the specified name
        """
        map = self.getMapByName2(name)
        if map:
            embed = getMapEmbed(map)
            await ctx.send(embed=embed)
        else:
            await ctx.send("I couldn't find that map, sorry!")

    # check for permissions here
    # or send request to admin?
    @commands.command()
    async def addNickname(self, ctx, *, name):
        """
        Adds a nickname to the specified Workshop Map
        """
        map = self.getMapByName(name)

        try:
            intro = f'So you want to add a nickname to the map "{map.name}" by {map.author}?'
            check = await self.checkTest(ctx, intro, "👎", ["👍", "👎"])

            if check:
                intro = "Great! What Nickname would you like to add?"
                try:
                    msg = await self.checkTest(ctx, intro)

                    # Need to add more validation to the actual nickname
                    nickname = msg.content
                    checkMaps = self.getMapByName(nickname)
                    if not checkMaps:
                        map.nicknames.append(nickname)
                        self.jsonUpdate()
                        await ctx.send("OK! Nickname added!")
                        embed = getMapEmbed(map)
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send(
                            f'Sorry! That nickname already belongs to "{checkMaps.name}" by {checkMaps.author}'
                        )
                except asyncio.TimeoutError:
                    await ctx.send(
                        "Looks like you didn't respond in time, pick a shorter nickname next time, ya dingus"
                    )
        except asyncio.TimeoutError:
            await ctx.send("👎")

    # check for permissions here
    @commands.command()
    async def removeNickname(self, ctx, *, name):
        """
        Removes the specified nickname from the map associated with it
        """
        map = self.getMapByName(name)

        if map.nicknames[0] is not name:
            intro = f'Would you like to remove the nickname "{name}" from  "{map.name}" by {map.author}?'
            negative = "Alright, well thanks for wasting my time I guess..."

            check = await self.checkTest(ctx, intro, negative, ["👍", "👎"])

            if check:
                map.nicknames.remove(name)
                self.jsonUpdate()
                await ctx.send("Nickname removed!")
        else:
            await ctx.send("The default name of the map cannot be removed")

    # Testing for generalizing checks
    @commands.command()
    async def test2(self, ctx):
        # map = self.workshopMaps[2]

        #test = any(d["userID"] == str(ctx.author.id) for d in map.trackingData["Data"])
        # test = next(d for d in map.trackingData["Data"] if d["userID"] == str(ctx.author.id))
        # print(type(map.trackingData["Data"][0]))
        # print(type(ctx.author.id))
        # print(map.trackingData["Data"][0]["userID"])

        for map in self.workshopMaps:
            print(map.nicknames)

    # check for permissions here
    #
    # NEED TO ADD WAY OF SPECIFYING DATA FORMATS
    #   also need to make sure measures are singular
    @commands.command()
    async def addMeasure(self, ctx, *, name):
        """
        Adds a way of measuring progress on a specified map
        """        
        map = self.getMapByName(name)

        intro = f'Would you like to add a progress metric to "{map.name}" by {map.author}?'
        negative = 'Oh, okay... Well I\'ll just be over here then...'

        check = await self.checkTest(ctx, intro, negative, ["👍", "👎"])

        if check:
            intro = 'Okay great! What would you like to add? Make sure your metric is in singular form'
            msg = await self.checkTest(ctx, intro)

            measure = msg.content.lower()

            # trackingData = map.trackingData
            if measure not in map.trackingData["type"]:
                map.trackingData["type"].append(measure)
                self.jsonUpdate
                await ctx.send(f'Alright I\'ve added "{measure}" to "{map.name}"')
            else:
                await ctx.send(f'Looks like {measure} is already in there, Whoops!')

    @commands.command()
    async def record(self, ctx, *, name):
        map = self.getMapByName(name)
        
        intro = f'Would you like to record progress for "{map.name}" by {map.author}?'
        negative = '....ALright then.'

        check = await self.checkTest(ctx, intro, negative, ["👍", "👎"])

        if check:
            if len(map.trackingData["type"]) == 0:
                # need to add measure
            else if len(map.trackingData["type"]) == 1:
                trackingType = map.trackingData["type"][0]
            else:
                prompt = "What would you like to record?"
                index = 1

                for t in map.trackingData["type"]:
                    prompt += f"\n{index} - {t}"
                    index += 1
                prompt += f"\n{index} - All of the above"

                msg = await self.checkTest(ctx, prompt)
                choice = int(msg.content)
            


            prompt = f"Enter new {map.trackingData[type][0]:}"

            input = await self.checkTest(ctx, prompt)
            data = input.content

            # validation here

            userData = next(d for d in map.trackingData["Data"] if d["userID"] == str(ctx.author.id))

            userData



# Functions

async def addMeasure(parameter_list):
    # Need to implement in the future in the case of 
    # first time map recordings
    pass

def getMapEmbed(map: _scraper.WorkshopMap):
    embed = discord.Embed(title=map.name)
    embed.set_thumbnail(url=map.imgLink)
    embed.add_field(name="Author", value=map.author, inline=False)
    embed.add_field(name="Description", value=map.description, inline=False)
    embed.add_field(
        name="Steam Link", value=f"steam://openurl/{map.mapLink}", inline=False
    )

    nicknameStr = ""
    for x in range(len(map.nicknames)):
        nicknameStr += map.nicknames[x]
        if x != (len(map.nicknames) - 1):
            nicknameStr += ", "

    embed.add_field(name="Nicknames", value=nicknameStr, inline=False)

    return embed


def parseJSON(data):
    maps = []
    for map in data["workshopMaps"]:
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
