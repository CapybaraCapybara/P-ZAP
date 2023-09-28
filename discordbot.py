import discord

TOKEN = 'Insert Bot Token Here'

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)

bot.run(TOKEN)
