import discord
from discord.ext import commands
import platform
from cogs import _json
import asyncio


class General(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("General Cog has been loaded...")

    # Commands

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def ping(self, ctx):
        """
        Returns current latency
        """
        # await ctx.send(f'Pong! latency: {round(client.latency * 1000)}ms')
        embed = discord.Embed(
            title="Pong!",
            description="It took {}ms.".format(round(self.client.latency * 1000)),
            color=0xFFFFFF,
        )

        await ctx.send(embed=embed)
        await ctx.send(f"Channel ID is {ctx.channel.id}")

    @commands.command()
    async def stats(self, ctx):
        """
        A useful command that displays bot statistics.
        """
        pythonVersion = platform.python_version()
        dpyVersion = discord.__version__
        serverCount = len(self.client.guilds)
        memberCount = len(set(self.client.get_all_members()))

        embed = discord.Embed(
            title=f"{self.client.user.name} Stats",
            description="\uFEFF",
            colour=ctx.author.colour,
            timestamp=ctx.message.created_at,
        )

        embed.add_field(name="Bot Version: ", value=self.client.version, inline=False)

        embed.add_field(name="Python Version: ", value=pythonVersion, inline=False)

        embed.add_field(name="Discord.py Version: ", value=dpyVersion, inline=False)

        embed.add_field(name="Total Servers: ", value=serverCount, inline=False)

        embed.add_field(name="Total Users: ", value=memberCount, inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def echo(self, ctx, *, message=None):
        """
        A simple command that repeats the users input back to them.
        """
        message = message or "Please provide the message to be repeated."
        await ctx.message.delete()
        await ctx.send(message)

    @commands.command(aliases=["disconnect", "close", "stopbot"])
    @commands.is_owner()
    async def logout(self, ctx):
        """
        If the user running the command owns the bot then this will disconnect the bot from discord.
        """
        await ctx.send(f"Hey {ctx.author.mention}, I am now logging out :wave:")
        await self.client.logout()

    @commands.command()
    @commands.is_owner()
    async def blacklist(self, ctx, user: discord.Member):
        if ctx.message.author.id == user.id:
            await ctx.send("Hey, you cannot blacklist yourself!")
            return

        self.client.blacklisted_users.append(user.id)
        data = _json.read_json("blacklist")
        data["blacklistedUsers"].append(user.id)
        _json.write_json(data, "blacklist")
        await ctx.send(f"Hey, I have blacklisted {user.name} for you.")

    @commands.command()
    @commands.is_owner()
    async def unblacklist(self, ctx, user: discord.Member):
        self.client.blacklisted_users.remove(user.id)
        data = _json.read_json("blacklist")
        data["blacklistedUsers"].remove(user.id)
        _json.write_json(data, "blacklist")
        await ctx.send(f"Hey, I have unblacklisted {user.name} for you.")

    @commands.command()
    async def test(self, ctx):
        await ctx.send("Please respond yes")

        def check(a):
            return a.author == ctx.author

        try:
            msg = await self.client.wait_for("message", check=check, timeout=5)

            str = "yes"
            if msg.content.lower() == str:
                await ctx.send("It worked! Yay!")
            else:
                await ctx.send(f'Hmm, "{msg.content}" doesn\'t look quite right..')
        except asyncio.TimeoutError:
            await ctx.send("Sorry! It looks like you didn't respond in time!")

    # Events

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = self.client.get_channel(708461726080827412)
        await channel.send(f"{member.mention} has joined the server!")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        channel = self.client.get_channel(708461726080827412)
        await channel.send(f"{member.mention} has left the server...")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """
        Global Error Handling
        """
        # Ignore these errors
        ignored = (commands.CommandNotFound, commands.UserInputError)
        if isinstance(error, ignored):
            return

        # Begin error handling
        if isinstance(error, commands.CommandOnCooldown):
            m, s = divmod(error.retry_after, 60)
            h, m = divmod(m, 60)
            if (int(h) == 0) and (int(m) == 0):
                await ctx.send(f" You must wait {int(s)} seconds to use this command!")
            elif (int(h) == 0) and (int(m) != 0):
                await ctx.send(
                    f" You must wait {int(m)} minutes and {int(s)} seconds to use this command!"
                )
            else:
                await ctx.send(
                    f" You must wait {int(h)} hours, {int(m)} minutes and {int(s)} seconds to use this command!"
                )
        elif isinstance(error, commands.CheckFailure):
            await ctx.send("Hey! You lack permission to use this command.")
        raise error


def setup(client):
    client.add_cog(General(client))
