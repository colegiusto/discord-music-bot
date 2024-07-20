import discord
from discord.ext import commands
import os

import asyncio
from yt_dlp import YoutubeDL as yd2

from youtubesearchpython import VideosSearch
from dotenv import dotenv_values







intents = discord.Intents.all()


client = commands.Bot(intents=intents, command_prefix="!")
token = dotenv_values(".env")['DISCORD_TOKEN']

queue = []
starting = False


def finish_track_func(file, ctx):
    async def func(arg):
        os.remove(file)
        if len(queue) > 0:
            await play_link_(ctx, queue.pop())
            return
        #await ctx.voice_client.disconnect()
    
    return func

@client.command()
async def man(ctx):
    with open('/home/pm/discord_bot_prod/man.txt', 'r') as man:
        await ctx.send(man.read())

@client.command()
async def test(ctx, arg):
    await ctx.send(arg+"2")

@client.command()
async def search(ctx, arg, play=True):
    videosSearch = VideosSearch(arg, limit = 2)
    videosResult = videosSearch.result()["result"][0]
    await ctx.send(videosResult['title']+ ": "+ videosResult["link"])
    if play:
        await play_link_(ctx, videosResult["link"])

@client.command()
async def q(ctx):
    if len(queue) < 0:
        await ctx.send("The queue is empty")
        return
    for x in queue:
        await ctx.send(x)


@client.command()
async def join(ctx):
    vc = ctx.author.voice
    if vc == None:
        await ctx.send("Not in channel")
        return
    await ctx.send("Suuurrrrreee")
    await vc.channel.connect()

@client.command()
async def l(ctx, link, random=True):
    with yd2({"extract_flat": False, "playlistrandom": random}) as ad:
        try:
            result = ad.extract_info(link, download=False)
        except Exception as ex:
            result = {}
        if not "entries" in result:
            await ctx.send("Playlist link failed")
            return
        ids = [i["id"] for i in result["entries"]]
        for id in ids:
            await play_link_(ctx, f"https://youtube.com/watch?v={id}")

@client.command()
async def play(ctx):
    if ctx.voice_client:
        ctx.voice_client.resume()

@client.command()
async def pause(ctx):
    if ctx.voice_client:
        ctx.voice_client.pause()

@client.command()
async def dc(ctx):
    global queue
    queue = []
    vc = ctx.voice_client
    if vc == None:
        await ctx.send("Not in channel")
        return
    await ctx.send("Suuurrrrreee")
    
    vclient = await vc.disconnect()

@client.command()
async def skip(ctx):
    ctx.voice_client.stop()

@client.command()
async def pl(ctx, link):
    await play_link_(ctx,link)
    return
    

async def play_link_(ctx,link:str):
    global starting
    if ctx.voice_client == None:
        if ctx.author.voice == None:
            await ctx.send("Not in channel")
            return
        await ctx.author.voice.channel.connect()
    if "list=" in link:
        link = link.split("list=")[0]
        await ctx.send("List link provided, playing only the first videopki")
    if ctx.voice_client.is_playing() or starting:
        queue.insert(0,link)
        return
    starting = True
    with yd2({'format':'bestaudio'}) as ad:
        info = ad.extract_info(link, False)
        if info["playlist"] != None:
            return
        file = ad.prepare_filename(info)
        ad.process_info(info_dict=info)
    
    source = await discord.FFmpegOpusAudio.from_probe(str(file), method="fallback")
    ctx.voice_client.play(source, after=lambda x: asyncio.run(finish_track_func(str(file), ctx)(x)))
    starting = False



@client.event
async def on_ready():
    print(f"{client.user} has connected to discord!")

client.run(token=token)
