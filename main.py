import os #reading auth file
import discord #discord bot
from dotenv import load_dotenv #discord auth
import asyncio

import scrape
import config
import datetime

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
	channel = client.get_channel(config.submissions_channel)
	while True:
		results = scrape.scrape_latest()
		for msg in results:
			print(msg)
			
			#create embed for Discord
			embed = discord.Embed(description=msg)
			await channel.send(embed=embed)
		
		await asyncio.sleep(config.submissions_frequency)

async def scrape_leaderboard(force = False):
	hours_checked = 0
	channel = client.get_channel(config.leaderboard_channel)
	while True:
		#we want the leaderboard scrape to only run around midnight UTC, so init a datetime
		now = datetime.datetime.utcnow()
		#and then check that it's 12:xx am (or if we've missed a cycle somehow)
		if(now.hour==0 or hours_checked>=24 or force):
			print("Running leaderboard scrape")
			results = scrape.scrape_leaderboard(force)
			#result should be a pure string
			print(results)
			
			#create embed for Discord
			#todo - decide if we want 3 leaderboards in one embed, or 3 separate embeds w/o title
			embed = discord.Embed(title="Leaderboards")
			embed.add_field(name="Mainboard", value=results)
			await channel.send(embed=embed)
			hours_checked = 0
		else:
			hours_checked += 1
		
		#and re-check hourly
		await asyncio.sleep(config.leaderboard_frequency)

@client.event
async def on_message(message):
	if message.author.discriminator != "1963" or message.author.name != "Sellyme":
		return

	#this block handles messages from the bot author that force update leaderboards
	#it's mostly for debugging purposes
	channel = client.get_channel(config.leaderboard_channel)
	if message.content == "!mainboard":
		await scrape_leaderboard(True)
	elif message.content == "!arcade":
		await channel.send("Feature not yet live")
	elif message.content == "!solution":
		await channel.send("Feature not yet live")
	elif message.content == "!rainbow":
		await channel.send("Feature not yet live")

client.run(TOKEN)