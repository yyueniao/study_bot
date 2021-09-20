import keep_alive
import discord
from discord.ext import commands
import asyncio
import os
from replit import db
import datetime


TOKEN = os.environ['TOKEN']
bot = commands.Bot(command_prefix='-')
end_time = {}


@bot.event
async def on_ready():
    print(">>机器人已到场<<")


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
    if not str(user.id) in db.keys():
      db[str(user.id)] = "0"
      db["number"] = str(int(db["number"])+1)
      db["rank"+db["number"]] = str(user.id)
      db[f"rank_of_{str(user.id)}"] = db["number"]
    db[str(user.id)] = str(int(db[str(user.id)]) + time)
    exp = int(db[str(user.id)])
    i = int(db[f"rank_of_{str(user.id)}"]) - 1

    while i > 0:
      rank_i = db[f"rank{str(i)}"]
      if int(db[rank_i]) < exp:
        db[f"rank{str(i+1)}"] = rank_i
        db[f"rank_of_{rank_i}"] = str(i+1)
      else:
        break
    db[f"rank{str(i+1)}"] = str(user.id)
    db[f"rank_of_{str(user.id)}"] = str(i+1)
    del end_time[user.id]
    await ctx.send(f"{user.mention}")
    await ctx.send(embed=embed)


@bot.command()
async def reset(ctx):
  keys = db.keys()
  for key in keys:
    del db[key]
  db["number"] = "0"


@bot.command()
async def rank(ctx):
  user = ctx.message.author
  rank = db[f"rank_of_{str(user.id)}"]
  embed = discord.Embed(title = "排名", description=f"{user.mention}: 第{rank}名")
  await ctx.send(embed=embed)


@bot.command()
async def leaderboard(ctx):
  number = int(db["number"])
  if number > 10:
    number = 10
  title = "学习排行榜"
  description = ""
  for i in range(number):
    description += f"{i+1}. "
    user_id = db["rank"+str(i+1)]
    exp = db[user_id]
    description += f"<@{user_id}>: {exp}分钟\n"
  embed = discord.Embed(title=title, description=description)
  await ctx.send(embed=embed)



if __name__ == "__main__":
  keep_alive.keep_alive()
  bot.run(TOKEN)
