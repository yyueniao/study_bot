import discord
from discord.ext import commands
import asyncpg
import asyncio
import os
import datetime


TOKEN = os.environ['TOKEN']
POSTGRES_URI = os.environ['POSTGRES_URI']
bot = commands.Bot(command_prefix='-s', intents=discord.Intents.all())
end_time = {}

pool = None


@bot.event
async def on_ready():
    global pool
    pool = await asyncpg.create_pool(POSTGRES_URI, ssl='require')

@bot.command()
async def pom(ctx, time=None):
    if ctx.message.author.id in end_time:
        await status(ctx)
        return 0
    if not (time and time.isdigit()):
        await ctx.send("请使用格式‘-pom [分钟]’\n例：‘-pom 30’")
        return 0
    if not int(time) >= 0:
        await ctx.send("请至少学习10分钟以上！不然人家懒得理你啦~")
        return 0
    title = f"{ctx.message.author.name}开始学习了！真棒！"
    description = f"这次学习时长为{time}分钟！加油！"
    embed_start = discord.Embed(title=title, description=description)
    end_time[ctx.message.author.id] = datetime.datetime.now() + datetime.timedelta(minutes=int(time))
    await ctx.send(f"{ctx.message.author.mention}")
    await ctx.send(embed=embed_start)
    await asyncio.sleep(int(time) * 60)
    await end(ctx, ctx.message.author, int(time))


@bot.command()
async def status(ctx):
    if not ctx.message.author.id in end_time:
        await ctx.send(f"{ctx.message.author.name}，您目前没有学习任务，现在马上开始学习吧！")
    else:
        time_remain = (end_time[ctx.message.author.id] - datetime.datetime.now()).seconds
        title = "任务进度"
        description = f"你正在学习任务中，这次任务还有{round(time_remain/60)}分钟就完成了，别放弃！"
        embed = discord.Embed(title=title, description=description)
        await ctx.send(embed=embed)


async def end(ctx, user, time):
    title = f"{user.name}完成学习了！休息一会吧~"
    description = f"你已经完成了{time}分钟的学习！"

    embed = discord.Embed(title=title, description=description)

    async with pool.acquire() as conn:
        record = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user.id)
        if not record:
            await conn.execute("INSERT INTO users (id, name) VALUES ($1, $2)", user.id, user.nick)   
            record = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user.id)
        
        await conn.execute("UPDATE users SET time = $1", record['time'] + time)

    await ctx.send(f"{user.mention}")
    await ctx.send(embed=embed)


@bot.command()
async def reset(ctx):
    async with pool.acquire() as conn:
        await conn.execute("TRUNCATE TABLE users")


@bot.command()
async def rank(ctx):
    async with pool.acquire() as conn:
        record = await conn.fetchrow('SELECT *, RANK() OVER ( ORDER BY time ) rank FROM users WHERE id = $1', ctx.author.id)
        rank = record['rank']

    await ctx.send(embed=discord.Embed(description=f"你是第{rank}名！"))


@bot.command()
async def leaderboard(ctx):
    lines = []
    async with pool.acquire() as conn:
        rows = await conn.fetch('SELECT *, RANK() OVER ( ORDER BY time DESC ) rank FROM users')
        for index, record in enumerate(rows):
            name = record['name']
            time = datetime.timedelta(seconds=record['time'])
            lines.append(f"{index + 1} {name}: {time}")

    description = "\n".join(lines)

    await ctx.send(embed=discord.Embed(title="学习排行榜", description=description)) 
            


if __name__ == "__main__":
    bot.run(TOKEN)
