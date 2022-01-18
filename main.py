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
	loop.create_task(scrape_leaderboards())

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

async def scrape_leaderboards():
	hours_checked = 0
	
	while True:
		#we want the leaderboard scrape to only run around midnight UTC, so init a datetime
		now = datetime.datetime.utcnow()
		#and then check that it's 12:xx am (or if we've missed a cycle somehow)
		if(now.hour==0 or hours_checked>=24):
			print("Running leaderboard scrape")

			await scrape_leaderboard("Mainboard")
			await scrape_leaderboard("Arcade")
			await scrape_leaderboard("Solution")
			await top_submitters()

			#reset 24hr timer
			hours_checked = 0
		else:
			hours_checked += 1

		#and re-check hourly
		await asyncio.sleep(config.leaderboard_frequency)
		

async def scrape_leaderboard(type, force = False):
	channel = client.get_channel(config.leaderboard_channel)

	results = scrape.scrape_leaderboard(type, force)
	#result should be a pure string
	print(results)

	#create embed for Discord
	embed = discord.Embed()
	embed.add_field(name=type, value=results)
	embed.timestamp = datetime.datetime.utcnow()
	await channel.send(embed=embed)

async def top_submitters(days):
	channel = client.get_channel(config.leaderboard_channel)
	
	results = scrape.scrape_top_submitters(days)
	#result should be a pure string
	print(results)
	
	#generate embed header
	if days == 1:
		fieldname = "Top submitters for today"
	else:
		fieldname = "Top submitters for the last " + str(days) + " days"
	
	#create embed for Discord
	embed = discord.Embed()
	embed.add_field(name=fieldname, value=results)
	embed.timestamp = datetime.datetime.utcnow()
	await channel.send(embed=embed)

@client.event
async def on_message(message):
	if message.author.discriminator != config.bot_owner_discriminator or message.author.name != config.bot_owner_name:
		return

	#this block handles messages from the bot author that force update leaderboards
	#it's mostly for debugging purposes
	channel = client.get_channel(config.leaderboard_channel)
	if message.content == "!mainboard":
		await scrape_leaderboard("Mainboard", True)
	elif message.content == "!arcade":
		await scrape_leaderboard("Arcade", True)
	elif message.content == "!solution":
		await scrape_leaderboard("Solution", True)
	elif message.content == "!rainbow":
		await channel.send("Feature not yet live")
	elif message.content.startswith("!submitters"):
		days = 1 #default parameter
		if len(message.content) > 11:
			#if there was a parameter added and we can parse that
			daysParam = message.content.lstrip("!submitters ")
			if daysParam.isnumeric():
				#isnumeric excludes negatives or decimals, which is good for this use case
				days = int(daysParam)

		await top_submitters(days)

client.run(TOKEN)