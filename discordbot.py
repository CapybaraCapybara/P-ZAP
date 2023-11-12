"""Discord Bot [Salapakjai] by P-ZAP"""
import logging
import os
from typing import Optional

import nextcord
from dotenv import load_dotenv
from nextcord.ext import commands

from utils import (
    generate_puzzle_embed,
    process_message_as_guess,
    random_puzzle_id,
    daily_puzzle_id
)

intents = nextcord.Intents.default()
intents.members = True
logging.basicConfig(level=logging.INFO)

load_dotenv()

activity = nextcord.Activity(type=nextcord.ActivityType.listening, name="/play")

bot = commands.Bot(command_prefix=commands.when_mentioned_or("w?"), activity=activity, intents=intents)

GUILD_IDS = (
    [int(guild_id) for guild_id in os.getenv("GUILD_IDS", "").split(",")]
    if os.getenv("GUILD_IDS", None)
    else nextcord.utils.MISSING
)

@bot.event
async def on_member_join(member):
    """แจ้งเตือนเมื่อคนเข้าเซิฟเวอร์"""
    guild = member.guild
    channel_name = "welcome"  #เปลี่ยนเป็นชื่อตาม Text channel ที่ต้องการส่ง
    channel = nextcord.utils.get(guild.text_channels, name=channel_name)

    if channel and channel.permissions_for(guild.me).send_messages:
        await channel.send(f"สวัสดีครับ {member.mention} ให้ผมนั่งคุยเป็นเพื่อนได้ไหมครับ")


@bot.event
async def on_member_remove(member):
    """แจ้งเตือนเมื่อคนออกเซิร์ฟเวอร์"""
    guild = member.guild
    channel_name = "welcome"  #เปลี่ยนเป็นชื่อตาม Text channel ที่ต้องการส่ง
    channel = nextcord.utils.get(guild.text_channels, name=channel_name)

    if channel and channel.permissions_for(guild.me).send_messages:
        await channel.send(f"ลาก่อนครับ {member.display_name}, หวังว่าจะได้พบกันอีกครั้งในอนาคต")

@bot.slash_command(name="play", description="Play Wordle Clone", guild_ids=GUILD_IDS)
async def slash_play(interaction: nextcord.Interaction):
    """คำสั่งสำหรับเล่นเกม"""
    pass


@slash_play.subcommand(name="random", description="Play a random game of Wordle Clone")
async def slash_play_random(interaction: nextcord.Interaction):
    """/play random"""
    embed = generate_puzzle_embed(interaction.user, random_puzzle_id())
    await interaction.send(embed=embed)

@slash_play.subcommand(name="daily", description="Play the daily game of Wordle Clone")
async def slash_play_daily(interaction: nextcord.Interaction):
    """/play daily"""
    embed = generate_puzzle_embed(interaction.user, daily_puzzle_id())
    await interaction.send(embed=embed)


@bot.group(invoke_without_command=True)
async def play(ctx: commands.Context, puzzle_id: Optional[int] = None):
    """เล่น Wordle game"""
    embed = generate_puzzle_embed(ctx.author, puzzle_id or random_puzzle_id())
    await ctx.reply(embed=embed, mention_author=False)


@play.command(name="random")
async def play_random(ctx: commands.Context):
    """เล่นแบบ Random"""
    embed = generate_puzzle_embed(ctx.author, random_puzzle_id())
    await ctx.reply(embed=embed, mention_author=False)


@play.command(name="daily")
async def play_daily(ctx: commands.Context):
    """เล่นรายวัน"""
    embed = generate_puzzle_embed(ctx.author, daily_puzzle_id())
    await ctx.reply(embed=embed, mention_author=False)


@bot.event
async def on_message(message: nextcord.Message):
    """วิเคราะห์ข้อความที่ส่งมา"""
    processed_as_guess = await process_message_as_guess(bot, message)
    if not processed_as_guess:
        await bot.process_commands(message)


bot.run(os.getenv("TOKEN"))
