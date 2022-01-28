import os #reading auth file
import discord #discord bot
from dotenv import load_dotenv #discord auth
import asyncio

import scrape
import config
from datetime import datetime, timedelta

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
	cs_channel = client.get_channel(config.cs_submissions_channel)
	ps_channel = client.get_channel(config.ps_submissions_channel)

	while True:
		results = scrape.scrape_latest()
		cs_results = results[0]
		ps_results = results[1]

		for msg in cs_results:
			print(msg)
			
			#create embed for Discord
			embed = discord.Embed(description=msg)
			await cs_channel.send(embed=embed)
			
		for msg in ps_results:
			#create embed for Discord
			embed = discord.Embed(description=msg)
			await ps_channel.send(embed=embed)
		
		await asyncio.sleep(config.submissions_frequency)

async def scrape_leaderboards():
	while True:
		f = open("last_leaderboards", "r+")
		last_scrape = f.read()
		last_scrape_dt = datetime.strptime(last_scrape, "%Y-%m-%d %H:%M:%S")
		lock_scrape = last_scrape_dt + timedelta(0.1)
		next_scrape = last_scrape_dt + timedelta(1)
		
	
		print("Checking leaderboard scrape")
		#we want the leaderboard scrape to only run around midnight UTC, so init a datetime
		now = datetime.utcnow()
		#and then check that it's 12:xx am (or if we've missed a cycle somehow)
		if (now.hour == 0 and lock_scrape < now) or next_scrape < now:
			print("Running leaderboard scrape")

			await scrape_leaderboard("Mainboard")
			await scrape_leaderboard("Arcade")
			await scrape_leaderboard("Solution")
			await top_submitters(1)

			#save the most recent scrape
			f.seek(0)
			f.write(now.strftime("%Y-%m-%d %H:%M:%S"))
			f.truncate()

		f.close()

		#and re-check hourly
		await asyncio.sleep(config.leaderboard_frequency)
		

async def scrape_leaderboard(type, force = False, idx = 0, channel_id = config.leaderboard_channel):
	channel = client.get_channel(channel_id)

	results = scrape.scrape_leaderboard(type, force, idx)
	#result should be a pure string
	print(results)

	#create embed for Discord
	embed = discord.Embed()
	embed.add_field(name=type, value=results)
	embed.timestamp = datetime.utcnow()
	await channel.send(embed=embed)

async def top_submitters(days = 1, channel_id = config.leaderboard_channel):
	channel = client.get_channel(channel_id)
	
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
	embed.timestamp = datetime.utcnow()
	await channel.send(embed=embed)

@client.event
async def on_message(message):
	#ignore messages from bots to avoid double-posting on PluralKit etc.
	if message.author.bot:
		return

	#we don't want to support any message requests in the NPS server
	if message.guild.id == config.cs_server_id:
		return

	if message.content.startswith("!mainboard"):
		await handle_mainboard(message)
	elif message.content.startswith("!arcade"):
		await handle_arcade(message)
	elif message.content.startswith("!solution"):
		await handle_solution(message)
	elif message.content.startswith("!rainbow"):
		await channel.send("Feature not yet live")
	elif message.content.startswith("!submitters"):
		await handle_submitters(message)

#todo - genericise these
async def handle_mainboard(message):
	idx = 0 #default parameter
	if len(message.content) > 10:
		#if there was a parameter added and we can parse that
		idxParam = message.content.lstrip("!mainboard ")
		if idxParam.isnumeric():
			#isnumeric excludes negatives or decimals, which is good for this use case
			idx = int(idxParam) - 1
	await scrape_leaderboard("Mainboard", True, idx, message.channel.id)

async def handle_arcade(message):
	idx = 0 #default parameter
	if len(message.content) > 7:
		#if there was a parameter added and we can parse that
		idxParam = message.content.lstrip("!arcade ")
		if idxParam.isnumeric():
			#isnumeric excludes negatives or decimals, which is good for this use case
			idx = int(idxParam) - 1
	await scrape_leaderboard("Arcade", True, idx, message.channel.id)
	
async def handle_solution(message):
	idx = 0 #default parameter
	if len(message.content) > 9:
		#if there was a parameter added and we can parse that
		idxParam = message.content.lstrip("!solution ")
		if idxParam.isnumeric():
			#isnumeric excludes negatives or decimals, which is good for this use case
			idx = int(idxParam) - 1
	await scrape_leaderboard("Solution", True, idx, message.channel.id)


async def handle_submitters(message):
	days = 1 #default parameter
	if len(message.content) > 11:
		#if there was a parameter added and we can parse that
		daysParam = message.content.lstrip("!submitters ")
		if daysParam.isnumeric():
			#isnumeric excludes negatives or decimals, which is good for this use case
			days = int(daysParam)

	await top_submitters(days, message.channel.id)

client.run(TOKEN)