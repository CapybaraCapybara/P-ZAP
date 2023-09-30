import discord

TOKEN = 'Insert Bot Token Here'

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = discord.Client(intents=intents)

@bot.event
async def on_member_join(member):
    guild = member.guild
    for channel in guild.text_channels:
        if channel and channel.permissions_for(guild.me).send_messages:
            await channel.send(f"สวัสดีครับ {member.mention} ให้ผมนั่งคุยเป็นเพื่อนได้ไหมครับ")

@bot.event
async def on_member_remove(member):
    guild = member.guild
    for channel in guild.text_channels:
        if channel and channel.permissions_for(guild.me).send_messages:
            await channel.send(f"ขอบคุณที่ให้ผมได้นั่งคุยเป็นเพื่อน {member.name}")

bot.run(TOKEN)
