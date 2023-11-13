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
async def on_ready():
    """แจ้งเตือนใน Terminal VSCode เมื่อบอทออนไลน์และพร้อมใช้งาน"""
    length1 = (len("Your bot is now online and ready to use"))
    length2 = (len("( Logged in as -> \"" + str(bot.user) + "\" )"))
    longest = max(length1, length2)

    print("-" * (longest+4))
    print("| " + "Your bot is now online and ready to use" + (" " * (longest - length1)) + " |")
    print("| " + f"( Logged in as -> \"{bot.user}\" )" + (" " * (longest - length2)) + " |")
    print("-" * (longest+4))

@bot.event
async def on_member_join(member):
    """แจ้งเตือนเมื่อคนเข้าเซิฟเวอร์"""
    guild = member.guild
    channel_name = "welcome"  #เปลี่ยนเป็นชื่อตาม Text channel ที่ต้องการส่ง
    channel = nextcord.utils.get(guild.text_channels, name=channel_name)
    if channel and channel.permissions_for(guild.me).send_messages:
        embed = nextcord.Embed(title=f" Welcome {member} 🎉!", description=f"ยินดีต้อนรับ {member.mention} \n เข้าสู่ {guild.name} \n ขอให้มีความสุขกับดิสคอร์ดแห่งนี้นะ!", color=0x00d9ff)
        embed.set_thumbnail(member.display_avatar)
        await channel.send(embed=embed)


@bot.event
async def on_member_remove(member):
    """แจ้งเตือนเมื่อคนออกเซิร์ฟเวอร์"""
    guild = member.guild
    channel_name = "welcome"  #เปลี่ยนเป็นชื่อตาม Text channel ที่ต้องการส่ง
    channel = nextcord.utils.get(guild.text_channels, name=channel_name)

    if channel and channel.permissions_for(guild.me).send_messages:
        embed = nextcord.Embed(title=f" Goodbye {member} 👋!", description=f"ลาก่อน  {member.mention} \n ขอบคุณที่เข้ามา แล้วไว้เจอกันใหม่นะ!", color=0xff0000)
        embed.set_thumbnail(member.display_avatar)
        await channel.send(embed=embed)

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

@bot.slash_command(name="play", description="เล่น Wordle", guild_ids=GUILD_IDS)
async def slash_play(interaction: nextcord.Interaction):
    """คำสั่งสำหรับเล่นเกม"""
    pass


@slash_play.subcommand(name="random", description="เล่น Wordle แบบสุ่ม")
async def slash_play_random(interaction: nextcord.Interaction):
    """/play random"""
    embed = generate_puzzle_embed(interaction.user, random_puzzle_id())
    await interaction.send(embed=embed)

@slash_play.subcommand(name="daily", description="เล่น Wordle แบบรายวัน")
async def slash_play_daily(interaction: nextcord.Interaction):
    """/play daily"""
    embed = generate_puzzle_embed(interaction.user, daily_puzzle_id())
    await interaction.send(embed=embed)

@slash_play.subcommand(name="id", description="เล่น Wordle โดยการใส่ ID")
async def slash_play_id(
    interaction: nextcord.Interaction,
    puzzle_id: int = nextcord.SlashOption(description="ใส่เลข ID ของคำเพื่อทาย"),
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

    player_card = [card["rank"] for card in player_hand]
    bot_card = bot_hand[0]['rank']

    embed = nextcord.Embed(title=f"ไพ่ของคุณ: {player_card}")
    await ctx.send(embed=embed)
    embed = nextcord.Embed(title=f"ไพ่ของบอท: {bot_card}", description=f"และหมอบไว้อีก 1 ใบ.")
    await ctx.send(embed=embed)

    while sum(get_card_value(card) for card in player_hand) < 21:
        hit_or_stand = await prompt_for_hit_or_stand(ctx)
        if hit_or_stand.lower() == 'hit':
            player_hand.append(draw_card(deck))
            player_card = [card["rank"] for card in player_hand]
            embed = nextcord.Embed(title=f"ไพ่ของคุณ: {player_card}")
            await ctx.send(embed=embed)
        else:
            break

    while sum(get_card_value(card) for card in bot_hand) < 17:
        bot_hand.append(draw_card(deck))

    bot_cards = [card["rank"] for card in bot_hand]
    embed = nextcord.Embed(title=f"ไพ่ของบอท: {bot_cards}")
    await ctx.send(embed=embed)

    result = determine_winner_bj(player_hand, bot_hand)
    embed = nextcord.Embed(title=f"{result}")
    await ctx.send(embed=embed)



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
    embed = nextcord.Embed(title="คุณต้องการที่จะ hit หรือ stand?", description="พิมพ์ `hit` หรือ `stand`.")
    await ctx.send(embed=embed)
    try:
        response = await bot.wait_for('message', timeout=30, check=lambda m: m.author == ctx.author and m.content.lower() in ['hit', 'stand'])
        return response.content.lower()
    except asyncio.TimeoutError:
        embed = nextcord.Embed(title="หมดเวลา", description="คุณเลือก stand")
        await ctx.send(embed=embed)
        return 'stand'

def get_card_value(card):
    """คำนวนค่าของไพ่"""
    if card["rank"].isdigit():
        return int(card["rank"])
    elif card["rank"] in ['J', 'Q', 'K']:
        return 10
    elif card["rank"] == 'A':
        return 11

def determine_winner_bj(player_hand, bot_hand):
    """ตัดสินผู้ชนะ"""
    player_sum = sum(get_card_value(card) for card in player_hand)
    bot_sum = sum(get_card_value(card) for card in bot_hand)

    if player_sum > 21:
        return 'คุณแต้มเกิน! บอทชนะ 💔'
    elif bot_sum > 21:
        return 'บอทแต้มเกิน! คุณชนะ! 🎉'
    elif player_sum > bot_sum:
        return 'คุณชนะ! 🎉'
    elif player_sum < bot_sum:
        return 'บอทชนะ 💔'
    else:
        return 'เสมอ!🤯'


# ========================================== ระบบเกมทายเลข ==========================================

@bot.command(name='gnum', help='เล่นเกมทายตัวเลข')
async def start_guessing_game(ctx):
    """เกมทายเลข"""
    embed = nextcord.Embed(title=f"ยินดีต้อนรับเข้าสู่เกมส์เดาตัวเลข!", description=f"เราได้สุ่มตัวเลขเพียง 1 ตัวจากตัวเลข 1 ถึง 100. \n ลองเดาตัวเลขนั้นดูสิ! แต่มีข้อแม้ว่าให้เดาได้แค่ 7 ครั้งนะ")
    await ctx.send(embed=embed)

    # สุ่มสร้างเลข 1 ตัวจากเลข 1 ถึง 100
    secret_number = random.randint(1, 100)

    # ให้ผู้เล่นสุ่มคำตอบได้ 7 ครั้ง
    guesschance = 7
    low, high = 1, 100
    for _ in range(7):
        guess = await prompt_for_guess(ctx, low, high, guesschance)
        if guess == secret_number:
            embed = nextcord.Embed(title="ยินดีด้วย! เดาได้ถูกต้อง", description=f"ตัวเลขนั้นคือ : {secret_number}", color=0x04ff00)
            await ctx.send(embed=embed)
            break
        elif guess < secret_number:
            low = guess + 1
            await ctx.send("ต่ำไปนะ! ลองเดาอีกที")
        else:
            high = guess - 1
            await ctx.send("สูงไปนะ! ลองเดาอีกที")
        guesschance -= 1
    else:
        await ctx.send(f"โชคไม่ดีเลย หมดโอกาสแล้ว. เลขที่ถูกต้องคือ {secret_number}.")
        embed = nextcord.Embed(title="โชคไม่ดีเลย หมดโอกาสแล้ว", description=f"เลขที่ถูกต้องคือ {secret_number}", color=0xff0000)
        await ctx.send(embed=embed)

async def prompt_for_guess(ctx, low, high, guesschance):
    """ตรวจสอบเลขที่ใส่มาและส่งกลับช่วงของตัวเลขที่เหลือ"""
    embed = nextcord.Embed(title=f"ตัวเลขนี้อยู่ระหว่าง {low} ถึง {high}:", description=f"เหลือโอกาสเดาอีก {guesschance} ครั้ง!")
    await ctx.send(embed=embed)

    try:
        guess = await bot.wait_for('message', timeout=30, check=lambda m: m.author == ctx.author)
        guess_number = int(guess.content)
        if low <= guess_number <= high:
            return guess_number
        else:
            await ctx.send("อยู่นอกช่วงที่ถูกต้อง ลองเดาใหม่อีกครั้ง!")
            return await prompt_for_guess(ctx, low, high, guesschance)
    except (nextcord.ext.commands.errors.CommandNotFound, ValueError):
        await ctx.send('อย่าใส่มั่วสิ! ใส่ตัวเลขลงไปสิ')
        return await prompt_for_guess(ctx, low, high, guesschance)

# ========================================== ระบบเกมเป่ายิงฉุบ ==========================================
total_streak = 0

@bot.command(name='rps', help="เกมเป่ายิ้งฉุบ")
async def rock_paper_scissors(ctx, user_choice):
    """เกมเป่ายิงฉุบ"""
    global total_streak

    user_choice = user_choice.lower()
    if user_choice not in ['ค้อน', 'กระดาษ', 'กรรไกร']:
        await ctx.send('ให้มันดีๆหน่อย. เลือกว่าจะออกอะไร ค้อน, กระดาษ, or กรรไกร.')
        return
    bot_choice = random.choice(['ค้อน', 'กระดาษ', 'กรรไกร'])
    result, colorrps = determine_winner_rps(user_choice, bot_choice)

    # ตรวจสอบผลลัพธ์และปรับจำนวนการชนะติดต่อกันทั้งหมด
    if result == 'คุณชนะ!':
        total_streak += 1
    else:
        total_streak = 0  # รีเซ็ตจำนวนการชนะเมื่อแพ้

    embed = nextcord.Embed(title=f"คุณเลือก {user_choice}, ฉันเลือก {bot_choice}", description=f"{result}", color=colorrps)
    embed.add_field(name="การชนะติดต่อกันทั้งหมด", value=total_streak)
    await ctx.send(embed=embed)

def determine_winner_rps(player, bot):
    """หาผู้ชนะเป่ายิงฉุบ"""
    if player == bot:
        return 'ดันเสมอ!', 0x787878
    elif (player == 'ค้อน' and bot == 'กรรไกร') or \
         (player == 'กระดาษ' and bot == 'ค้อน') or \
         (player == 'กรรไกร' and bot == 'กระดาษ'):
        return 'คุณชนะ!', 0x04ff00
    else:
        return 'ฉันชนะ!', 0xff0000

bot.run(os.getenv("TOKEN"))
