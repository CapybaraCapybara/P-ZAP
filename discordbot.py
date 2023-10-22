"""Discord Bot [Salapakjai] by P-ZAP"""
import discord
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
)

logging.basicConfig(level=logging.INFO)

load_dotenv()

activity = nextcord.Activity(type=nextcord.ActivityType.listening, name="/play")

bot = commands.Bot(command_prefix=commands.when_mentioned_or("w?"), activity=activity)

GUILD_IDS = (
    [int(guild_id) for guild_id in os.getenv("GUILD_IDS", "").split(",")]
    if os.getenv("GUILD_IDS", None)
    else nextcord.utils.MISSING
)


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = discord.Client(intents=intents)

@bot.event #แจ้งเตือนใน Terminal ใน VS Code เมื่อ bot online
async def on_ready():
    print("------------------------------------------------------------")
    print(f"Your bot is now online -(Logged in as {bot.user})")

@bot.event #แจ้งเตือนคนเข้าเซิร์ฟเวอร์
async def on_member_join(member):
    guild = member.guild
    for channel in guild.text_channels:
        if channel and channel.permissions_for(guild.me).send_messages:
            await channel.send(f"สวัสดีครับ {member.mention} ให้ผมนั่งคุยเป็นเพื่อนได้ไหมครับ")

@bot.event #แจ้งเตือนคนออกจากเซิร์ฟเวอร์
async def on_member_remove(member):
    guild = member.guild
    for channel in guild.text_channels:
        if channel and channel.permissions_for(guild.me).send_messages:
            await channel.send(f"ขอบคุณที่ให้ผมได้นั่งคุยเป็นเพื่อน {member.name}")

   
@bot.slash_command(name="play", description="Play Wordle Clone", guild_ids=GUILD_IDS)
async def slash_play(interaction: nextcord.Interaction):
    """คำสั่งสำหรับเล่นเกม"""
    pass


@slash_play.subcommand(name="random", description="Play a random game of Wordle Clone")
async def slash_play_random(interaction: nextcord.Interaction):
    embed = generate_puzzle_embed(interaction.user, random_puzzle_id())
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

    
@bot.event
async def on_message(message: nextcord.Message):

    #วิเคราะห์ข้อความที่ส่งมา

    processed_as_guess = await process_message_as_guess(bot, message)
    if not processed_as_guess:
        await bot.process_commands(message)


bot.run(os.getenv("TOKEN"))
