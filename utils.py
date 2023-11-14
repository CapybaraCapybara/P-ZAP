import nextcord
import datetime
import random
import re
from typing import List, Optional

popular_words = open("dict-popular.txt").read().splitlines()
all_words = set(word.strip() for word in open("dict-sowpods.txt"))

#แทนที่อักษรต่างๆด้วยอีโมจิที่เก็บไว้ในดิสคอร์ดอื่น
EMOJI_CODES = {
    "green": {
        "a": "<:1f1e6:1162729977767284776>",
        "b": "<:1f1e7:1162729981684752506>",
        "c": "<:1f1e8:1162729989070925835>",
        "d": "<:1f1e9:1162729994519314482>",
        "e": "<:1f1ea:1162729997807653027>",
        "f": "<:1f1eb:1162730002488512562>",
        "g": "<:1f1ec:1162730006133350403>",
        "h": "<:1f1ed:1162730008339554394>",
        "i": "<:1f1ee:1162730011929890906>",
        "j": "<:1f1ef:1162730015469867049>",
        "k": "<:1f1f0:1162730018187780167>",
        "l": "<:1f1f1:1162730021824237648>",
        "m": "<:1f1f2:1162730025515221032>",
        "n": "<:1f1f3:1162730029554352229>",
        "o": "<:1f1f4:1162730031915745370>",
        "p": "<:1f1f5:1162730035774500935>",
        "q": "<:1f1f6:1162730037989085306>",
        "r": "<:1f1f7:1162730041461985360>",
        "s": "<:1f1f8:1162730044939042886>",
        "t": "<:1f1f9:1162730047136874536>",
        "u": "<:1f1fa:1162730050920136735>",
        "v": "<:1f1fb:1162730055278018650>",
        "w": "<:1f1fc:1162730059048697877>",
        "x": "<:1f1fd:1162730061552701520>",
        "y": "<:1f1fe:1162730255279194132>",
        "z": "<:1f1ff:1162730258970181672>",
    },
    "yellow": {
        "a": "<:1f1e6:1162730295641002035>",
        "b": "<:1f1e7:1162730297272574044>",
        "c": "<:1f1e8:1162730301479465082>",
        "d": "<:1f1e9:1162730304784572416>",
        "e": "<:1f1ea:1162730308408451143>",
        "f": "<:1f1eb:1162730310342025297>",
        "g": "<:1f1ec:1162730313785540649>",
        "h": "<:1f1ed:1162730317724004444>",
        "i": "<:1f1ee:1162730319410110476>",
        "j": "<:1f1ef:1162730323575050291>",
        "k": "<:1f1f0:1162730326825652434>",
        "l": "<:1f1f1:1162730328939581460>",
        "m": "<:1f1f2:1162730332672495726>",
        "n": "<:1f1f3:1162730336086663208>",
        "o": "<:1f1f4:1162730338464833598>",
        "p": "<:1f1f5:1162730342428463104>",
        "q": "<:1f1f6:1162730345729368134>",
        "r": "<:1f1f7:1162730349843984487>",
        "s": "<:1f1f8:1162730357049802752>",
        "t": "<:1f1f9:1162730360367497247>",
        "u": "<:1f1fa:1162730362422710323>",
        "v": "<:1f1fb:1162730365765554236>",
        "w": "<:1f1fc:1162730369381052417>",
        "x": "<:1f1fd:1162730371293642793>",
        "y": "<:1f1fe:1162730374720405515>",
        "z": "<:1f1ff:1162730379250241557>",
    },
    "gray": {
        "a": "<:1f1e6:1162729741296599100>",
        "b": "<:1f1e7:1162729744903704636>",
        "c": "<:1f1e8:1162729746782769342>",
        "d": "<:1f1e9:1162729750318555166>",
        "e": "<:1f1ea:1162729753632067614>",
        "f": "<:1f1eb:1162729755381084202>",
        "g": "<:1f1ec:1162729760447811615>",
        "h": "<:1f1ed:1162729766621823006>",
        "i": "<:1f1ee:1162729770006614140>",
        "j": "<:1f1ef:1162729772128936066>",
        "k": "<:1f1f0:1162729775392112711>",
        "l": "<:1f1f1:1162729779213111437>",
        "m": "<:1f1f2:1162729781280915556>",
        "n": "<:1f1f3:1162729785118695524>",
        "o": "<:1f1f4:1162729789329768478>",
        "p": "<:1f1f5:1162729793251454986>",
        "q": "<:1f1f6:1162729795512180766>",
        "r": "<:1f1f7:1162729799157031013>",
        "s": "<:1f1f8:1162729802663465050>",
        "t": "<:1f1f9:1162729804903239681>",
        "u": "<:1f1fa:1162729809584062504>",
        "v": "<:1f1fb:1162729814499786762>",
        "w": "<:1f1fc:1162729818845102140>",
        "x": "<:1f1fd:1162729820942250074>",
        "y": "<:1f1fe:1162729824733904966>",
        "z": "<:1f1ff:1162729827925757994>",
    },
}


def generate_colored_word(guess: str, answer: str) -> str:
    """สร้าง string emoji code ที่แทนที่ตัวอักษร"""
    # - อักษรเหมือนกัน, ที่เดียวกัน: Green
    # - อักษรเหมือนกัน, คนละที่: Yellow
    # - อักษรไม่เหมือนกัน: Gray
    colored_word = [EMOJI_CODES["gray"][letter] for letter in guess]
    guess_letters: List[Optional[str]] = list(guess)
    answer_letters: List[Optional[str]] = list(answer)
    # เปลี่ยนสีเป็นสีเขียวเมื่ออยู่ตำแหน่งเดียวกัน
    for i in range(len(guess_letters)):
        if guess_letters[i] == answer_letters[i]:
            colored_word[i] = EMOJI_CODES["green"][guess_letters[i]]
            answer_letters[i] = None
            guess_letters[i] = None
    # เปลี่ยนเป็นสีเหลืองเมื่อตัวเดียวกันแต่อยู่คนละที่
    for i in range(len(guess_letters)):
        if guess_letters[i] is not None and guess_letters[i] in answer_letters:
            colored_word[i] = EMOJI_CODES["yellow"][guess_letters[i]]
            answer_letters[answer_letters.index(guess_letters[i])] = None
    return "".join(colored_word)


def generate_blanks() -> str:
    """สร้างอีโมจิปล่าวๆ 5 ตัว"""
    return ":white_medium_square:" * 5


def generate_puzzle_embed(user: nextcord.User, puzzle_id: int) -> nextcord.Embed:
    """สร้าง embed สำหรับ puzzle อันใหม่ สำหรับ puzzle id และ user"""
    embed = nextcord.Embed(title="Wordle Game")
    embed.description = "\n".join([generate_blanks()] * 6)
    embed.set_author(name=user.name, icon_url=user.display_avatar.url)
    embed.set_footer(
        text=f"ID: {puzzle_id} ︱ ใช้คำสั่ง /play! เพื่อเล่น\n"
        "เพื่อที่จะตอบ, ตอบกลับข้อความนี้ เพื่อทาย"
    )
    return embed


def update_embed(embed: nextcord.Embed, guess: str) -> nextcord.Embed:
    """อัปเดตคำศัพท์"""
    puzzle_id = int(embed.footer.text.split()[1])
    answer = popular_words[puzzle_id]
    colored_word = generate_colored_word(guess, answer)
    empty_slot = generate_blanks()
    # แทนที่ช่องแรกด้วย color emoji
    embed.description = embed.description.replace(empty_slot, colored_word, 1)
    # เช็ค game over
    num_empty_slots = embed.description.count(empty_slot)
    if guess == answer:
        if num_empty_slots == 0:
            embed.description += "\n\nปิ้วๆๆ!"
        if num_empty_slots == 1:
            embed.description += "\n\nเก่งมาก!"
        if num_empty_slots == 2:
            embed.description += "\n\nยอดเยี่ยมมาก!"
        if num_empty_slots == 3:
            embed.description += "\n\nน่าประทับใจ!"
        if num_empty_slots == 4:
            embed.description += "\n\nมหัศจรรย์!"
        if num_empty_slots == 5:
            embed.description += "\n\nอัจริยะ!"
    elif num_empty_slots == 0:
        embed.description += f"\n\nคำตอบคือ {answer}!"
    return embed


def is_valid_word(word: str) -> bool:
    """เช็คคำที่ไม่มีอยู่ในลิส"""
    return word in all_words


def random_puzzle_id() -> int:
    """สร้างคำจาก ID"""
    return random.randint(0, len(popular_words) - 1)


def daily_puzzle_id() -> int:
    """สร้างคำจาก Daily"""
    # คำนวนวันตั้งแต่ 1/1/2022 และ mod จำนวนของ puzzle

    num_words = len(popular_words)
    time_diff = datetime.datetime.now().date() - datetime.date(2022, 1, 1)
    return time_diff.days % num_words


def is_game_over(embed: nextcord.Embed) -> bool:
    """เช็ค game over ใน embed"""
    return "\n\n" in embed.description


async def process_message_as_guess(bot: nextcord.Client, message: nextcord.Message) -> bool:
    """เช็คว่า message ที่ส่งไป reply กับ Wordle bot ตรวจสอบความถูกต้องและอัปเดตข้อความของบอท"""
    # รับ message ที่ reply
    ref = message.reference
    if not ref or not isinstance(ref.resolved, nextcord.Message):
        return False
    parent = ref.resolved

    # ถ้าไม่ใช่ ก็ ignore มัน
    if parent.author.id != bot.user.id:
        return False

    # เช็คว่ามัน embed หรือไม่ 
    if not parent.embeds:
        return False

    embed = parent.embeds[0]
    guess = message.content.lower()

    # เช็คว่าใช่ผู้เล่นที่ใช่งานอยู่รึปล่าว
    if (
        embed.author.name != message.author.name
        or embed.author.icon_url != message.author.display_avatar.url
    ):
        reply = "เริ่มเกมใหม่ด้วยคำสั่ง /play"
        if embed.author:
            reply = f"This game was started by {embed.author.name}. " + reply
        await message.reply(reply, delete_after=5)
        try:
            await message.delete(delay=5)
        except Exception:
            pass
        return True

    # เช็คว่า game over รึยัง
    if is_game_over(embed):
        await message.reply("The game is already over. Start a new game with /play", delete_after=5)
        try:
            await message.delete(delay=5)
        except Exception:
            pass
        return True

    # ตัด mention สำหรับผู้เล่นออก
    guess = re.sub(r"<@!?\d+>", "", guess).strip()
    bot_name = message.guild.me.nick if message.guild and message.guild.me.nick else bot.user.name

    if len(guess) == 0:
        await message.reply(
            "I am unable to see what you are trying to guess.\n"
            "Please try mentioning me in your reply before the word you want to guess.\n\n"
            f"**For example:**\n{bot.user.mention} crate\n\n"
            f"To bypass this restriction, you can start a game with `@\u200b{bot_name} play` instead of `/play`",
            delete_after=14,
        )
        try:
            await message.delete(delay=14)
        except Exception:
            pass
        return True

    # เช็คความยาวคำ
    if len(guess.split()) > 1:
        await message.reply("Please respond with a single 5-letter word.", delete_after=5)
        try:
            await message.delete(delay=5)
        except Exception:
            pass
        return True

    # เช็คคำศัพท์ว่าอยู่ในลิสหรือไม่
    if not is_valid_word(guess):
        await message.reply("That is not a valid word", delete_after=5)
        try:
            await message.delete(delay=5)
        except Exception:
            pass
        return True

    # อัปเดตคำศัพท์
    embed = update_embed(embed, guess)
    await parent.edit(embed=embed)

    # ลบข้อความ
    try:
        await message.delete()
    except Exception:
        pass

    return True
