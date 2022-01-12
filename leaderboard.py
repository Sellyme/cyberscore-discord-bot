import os #reading auth file
import discord #discord bot
from dotenv import load_dotenv #discord auth
import asyncio #timer

import scrape
import config

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()
@client.event
async def on_ready():
	print(client.user, "has connected to Discord!")
	await scrape_leaderboard()

async def scrape_leaderboard():
	channel = client.get_channel(config.test_channel)
	while True:
		results = scrape.scrape_leaderboard()
		#result should be a pure string
		print(results)
		
		#create embed for Discord
		embed = discord.Embed(description=results)
		await channel.send(embed=embed)
		
		#and only run this every 24 hours
		await asyncio.sleep(config.leaderboard_frequency)

client.run(TOKEN)