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

	await scrape_latest()

async def scrape_latest():
	cs_channel = client.get_channel(config.rss_channel)
	while True:
		results = scrape.scrape()
		for msg in results:
			print(msg)
			
			#create embed for Discord
			embed = discord.Embed(description=msg)
			await cs_channel.send(embed=embed)
		
		await asyncio.sleep(config.scrape_frequency)




client.run(TOKEN)