import os #reading auth file
import discord #discord bot
from dotenv import load_dotenv #discord auth
import asyncio
import scrape

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

@client.event
async def on_ready():
	print(client.user, " has connected to Discord!")

	await scrape_latest()

async def scrape_latest():
	cs_channel = client.get_channel(930473063043178586)
	while True:
		results = scrape.scrape()
		for msg in results:
			print(msg)
			await cs_channel.send(msg)
		
		await asyncio.sleep(120)




client.run(TOKEN)