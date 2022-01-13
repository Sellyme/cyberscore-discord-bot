import os #reading auth file
import discord #discord bot
from dotenv import load_dotenv #discord auth
import asyncio

import scrape
import config

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

@client.event
async def on_ready():
	print(client.user, "has connected to Discord!")

	loop = asyncio.get_event_loop()
	loop.create_task(scrape_latest())
	loop.create_task(scrape_leaderboard())

async def scrape_latest():
	channel = client.get_channel(config.rss_channel)
	while True:
		results = scrape.scrape_latest()
		for msg in results:
			print(msg)
			
			#create embed for Discord
			embed = discord.Embed(description=msg)
			await channel.send(embed=embed)
		
		await asyncio.sleep(config.submissions_frequency)

async def scrape_leaderboard():
	print("Running leaderboard scrape")
	channel = client.get_channel(config.test_channel)
	while True:
		results = scrape.scrape_leaderboard()
		#result should be a pure string
		print(results)
		
		#create embed for Discord
		#todo - decide if we want 3 leaderboards in one embed, or 3 separate embeds w/o title
		embed = discord.Embed(title="Leaderboards")
		embed.add_field(name="Mainboard", value=results)
		await channel.send(embed=embed)
		
		#and only run this every 24 hours
		await asyncio.sleep(config.leaderboard_frequency)

client.run(TOKEN)