import discord
from discord.ext import commands
import asyncio
import json


with open("setting.json", 'r', encoding='utf8') as jfile:
    jdata = json.load(jfile)

bot = commands.Bot(command_prefix='-')


@bot.event
async def on_ready():
    print(">>机器人已到场<<")


@bot.command()
async def pom(ctx, time=None):
    if not (time and time.isdigit()):
        await ctx.send("请使用格式‘-pom [分钟]’\n例：‘-pom 30’")
        return 0
    if not int(time) >= 10:
        await ctx.send("请至少学习10分钟以上！不然人家懒得理你啦~")
        return 0
    title = f"{ctx.message.author.name}开始学习了！真棒！"
    description = f"这次学习时长为{time}分钟！加油！"
    embed_start = discord.Embed(title=title, description=description)
    await ctx.send(f"{ctx.message.author.mention}")
    await ctx.send(embed=embed_start)
    await asyncio.sleep(int(time) * 60)
    await end(ctx, ctx.message.author, int(time))


async def end(ctx, user, time):
    title = f"{user.name}完成学习了！休息一会吧~"
    description = f"你已经完成了{time}分钟的学习！"
    embed = discord.Embed(title=title, description=description)
    await ctx.send(f"{user.mention}")
    await ctx.send(embed=embed)


if __name__ == "__main__":
    bot.run(jdata["TOKEN"])
