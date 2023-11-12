"""Discord Bot [Salapakjai] by P-ZAP"""
import logging
import os
from typing import Optional
import random
import asyncio
import datetime
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
intents.message_content = True
logging.basicConfig(level=logging.INFO)

load_dotenv()

activity = nextcord.Activity(type=nextcord.ActivityType.listening, name="/play")

bot = commands.Bot(command_prefix=commands.when_mentioned_or("w?"), activity=activity, intents=intents)
bot = commands.Bot(command_prefix="/", intents=intents)


GUILD_IDS = (
    [int(guild_id) for guild_id in os.getenv("GUILD_IDS", "").split(",")]
    if os.getenv("GUILD_IDS", None)
    else nextcord.utils.MISSING
)


# ========================================== ระบบแจ้งเตือนต่างๆ ==========================================

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

@bot.event
async def on_voice_state_update(member, before, after):
    """แจ้งเตือนเมื่อคนเข้าออกช่องพูดคุย"""
    guild = member.guild
    channel_name = "vc-log"  #เปลี่ยนเป็นชื่อตาม Text channel ที่ต้องการส่ง
    channel = nextcord.utils.get(guild.text_channels, name=channel_name)
    voicechannel = bot.get_channel(1173175465113038918) #เปลี่ยนเลขตาม Voice Channel ID
    time1 = datetime.datetime.now()
    timenow = time1.strftime("%H:%M:%S  -  %d %B %Y")
    if before.channel != after.channel: #เข้า
        if after.channel is not None and after.channel.id == 1173175465113038918: #เปลี่ยนเลขตาม Voice Channel ID
            embed = nextcord.Embed(title=f"{member.name} ได้เข้ามาสู่ {voicechannel.name}", description=f"เมื่อเวลา {timenow} \n จะมีใครเข้ามาอยู่เป็นเพื่อนเขาไหมนะ?")
            await channel.send(embed=embed)
    if before.channel != after.channel: #ออก
        if before.channel is not None and before.channel.id == 1173175465113038918: #เปลี่ยนเลขตาม Voice Channel ID
            embed = nextcord.Embed(title=f"{member.name} ออกจาก {voicechannel.name}", description=f"เมื่อเวลา {timenow} \n Bon Voyage ไว้เจอกันใหม่นะเพื่อน")
            await channel.send(embed=embed)


# ========================================== ระบบเกม Wordle ==========================================

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

@slash_play.subcommand(name="id", description="Play a game of Wordle Clone by its ID")
async def slash_play_id(
    interaction: nextcord.Interaction,
    puzzle_id: int = nextcord.SlashOption(description="Puzzle ID of the word to guess"),
):
    """/play id"""
    embed = generate_puzzle_embed(interaction.user, puzzle_id)
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

@play.command(name="id")
async def play_id(ctx: commands.Context, puzzle_id: int):
    """เล่นจาก ID"""
    embed = generate_puzzle_embed(ctx.author, puzzle_id)
    await ctx.reply(embed=embed, mention_author=False)

@bot.event
async def on_message(message: nextcord.Message):
    """วิเคราะห์ข้อความที่ส่งมา"""
    processed_as_guess = await process_message_as_guess(bot, message)
    if not processed_as_guess:
        await bot.process_commands(message)


# ========================================== ระบบเกม BLACKJACK ==========================================

@bot.command(name='bj', help='เล่นแบล็กแจ็คกับบอท')
async def play_blackjack(ctx):
    """เกม Blackjack"""
    deck = create_deck()
    player_hand = [draw_card(deck), draw_card(deck)]
    bot_hand = [draw_card(deck), draw_card(deck)]

    await ctx.send(f'ไพ่ของคุณ: {[card["rank"] for card in player_hand]}')
    await ctx.send(f"ไพ่บอท: {bot_hand[0]['rank']} และหมอบไว้อีก 1 ใบ.")

    while sum(get_card_value(card) for card in player_hand) < 21:
        hit_or_stand = await prompt_for_hit_or_stand(ctx)
        if hit_or_stand.lower() == 'hit':
            player_hand.append(draw_card(deck))
            await ctx.send(f'ไพ่ของคุณ: {[card["rank"] for card in player_hand]}')
        else:
            break

    while sum(get_card_value(card) for card in bot_hand) < 17:
        bot_hand.append(draw_card(deck))

    await ctx.send(f'ไพ่บอท: {[card["rank"] for card in bot_hand]}')

    result = determine_winner(player_hand, bot_hand)
    await ctx.send(result)

def create_deck():
    """สร้างเด็คไพ่"""
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    deck = [{'rank': rank, 'suit': suit} for rank in ranks for suit in suits]
    random.shuffle(deck)
    return deck

def draw_card(deck):
    """สุ่มไพ่"""
    return deck.pop()

async def prompt_for_hit_or_stand(ctx):
    """เลือก Action"""
    await ctx.send('คุณต้องการที่จะ hit หรือ stand? พิมพ์ `hit` หรือ `stand`.')
    try:
        response = await bot.wait_for('message', timeout=30, check=lambda m: m.author == ctx.author and m.content.lower() in ['hit', 'stand'])
        return response.content.lower()
    except asyncio.TimeoutError:
        await ctx.send('หมดเวลา, คุณเลือก stand')
        return 'stand'

def get_card_value(card):
    """คำนวนค่าของไพ่"""
    if card["rank"].isdigit():
        return int(card["rank"])
    elif card["rank"] in ['J', 'Q', 'K']:
        return 10
    elif card["rank"] == 'A':
        return 11

def determine_winner(player_hand, bot_hand):
    """ตัดสินผู้ชนะ"""
    player_sum = sum(get_card_value(card) for card in player_hand)
    bot_sum = sum(get_card_value(card) for card in bot_hand)

    if player_sum > 21:
        return 'คุณแต้มเกิน! บอทชนะ'
    elif bot_sum > 21:
        return 'บอทแต้มเกิน! คุณชนะ'
    elif player_sum > bot_sum:
        return 'คุณชนะ!'
    elif player_sum < bot_sum:
        return 'บอทชนะ'
    else:
        return 'เสมอ!'


# ========================================== ระบบเกมทายเลข ==========================================

@bot.command(name='start', help='Start a guessing game')
async def start_guessing_game(ctx):
    """เกมทายเลข"""
    await ctx.send("ยินดีต้อนรับเข้าสู่เกมส์เดาตัวเลข! เราได้สุ่มตัวเลขเพียง 1 ตัวจากตัวเลข 1 ถึง 100. ลองเดาตัวเลขนั้นดูสิ!")

    # สุ่มสร้างเลข 1 ตัวจากเลข 1 ถึง 100
    secret_number = random.randint(1, 100)

    # ให้ผู้เล่นสุ่มคำตอบได้ 7 ครั้ง
    for _ in range(7):
        guess = await prompt_for_guess(ctx)
        if guess == secret_number:
            await ctx.send(f"ยินดีด้วย! เดาได้ถูกต้อง ตัวเลขนัั้นคือ : {secret_number}")
            break
        elif guess < secret_number:
            await ctx.send("ต่ำไปนะ! ลองเดาอีกที")
        else:
            await ctx.send("สูงไปนะ! ลองเดาอีกที")
    else:
        await ctx.send(f"โชคไม่ดีเลย หมดโอกาสแล้ว. เลขที่ถูกต้องคือ {secret_number}.")

async def prompt_for_guess(ctx):
    """ตรวจสอบเลขที่ใส่มา"""
    await ctx.send("ตัวเลขนี้อยู่ระหว่าง 1 ถึง 100:")
    try:
        guess = await bot.wait_for('message', timeout=30, check=lambda m: m.author == ctx.author)
        return int(guess.content)
    except (nextcord.ext.commands.errors.CommandNotFound, ValueError):
        await ctx.send('อย่าใส่มั่วสิ. ใส่ตัวเลขลงไปสิ')
        return await prompt_for_guess(ctx)


# ========================================== ระบบเกมเป่ายิงฉุบ ==========================================

@bot.command(name='rps')
async def rock_paper_scissors(ctx, user_choice):
    """เกมเป่ายิงฉุบ"""
    user_choice = user_choice.lower()
    if user_choice not in ['ค้อน', 'กระดาษ', 'กรรไกร']:
        await ctx.send('ให้มันดีๆหน่อย. เลือกว่าจะออกอะไร ค้อน, กระดาษ, or กรรไกร.')
        return
    bot_choice = random.choice(['ค้อน', 'กระดาษ', 'กรรไกร'])
    result = determine_winner(user_choice, bot_choice)
    await ctx.send(f'คุณเลือก {user_choice}, ฉันเลือก {bot_choice}. {result}')

def determine_winner(player, bot):
    """หาผู้ชนะเป่ายิงฉุบ"""
    if player == bot:
        return 'ดันเสมอ!'
    elif (player == 'ค้อน' and bot == 'กรรไกร') or \
         (player == 'กระดาษ' and bot == 'ค้อน') or \
         (player == 'กรรไกร' and bot == 'กระดาษ'):
        return 'คุณชนะ!'
    else:
        return 'ฉันชนะ!'

bot.run(os.getenv("TOKEN"))
