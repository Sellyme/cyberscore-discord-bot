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

			top10_change = False

			#if any of the important leaderboards have position changes, track them
			top10_change = (await scrape_leaderboard("Starboard") or
			await scrape_leaderboard("Rainbow") or
			await scrape_leaderboard("Arcade") or
			await scrape_leaderboard("Solution") or
			await scrape_leaderboard("Challenge") or
			await scrape_leaderboard("Proof") or
			await scrape_leaderboard("Video"))
			#and then also run the remaining leaderboards
			await scrape_leaderboard("Submissions")
			await top_submitters(1)

			#save the most recent scrape
			f.seek(0)
			f.write(now.strftime("%Y-%m-%d %H:%M:%S"))
			f.truncate()
			
			#finally, print out a role ping if there was a positional change
			if top10_change:
				channel = client.get_channel(config.leaderboard_channel)
				await channel.send("<@&951246251427520512>")

		f.close()


		#and re-check hourly
		await asyncio.sleep(config.leaderboard_frequency)
		

async def scrape_leaderboard(type, force = False, idx = 0, channel_id = config.leaderboard_channel):
	channel = client.get_channel(channel_id)

	results = scrape.scrape_leaderboard(type, force, idx)
	#result should be a pure string
	print(results)
	if type == "Submissions" and not force:
		#this board isn't too useful to output daily since the 24hr submitters board exists
		return
	elif type == "Video":
		#more user-friendly name for the embed title
		name = "Video Proof"
	else:
		name = type

	#create embed for Discord
	embed = discord.Embed()
	embed.add_field(name=name, value=results)
	embed.timestamp = datetime.utcnow()
	await channel.send(embed=embed)
	
	#and indicate whether or not there was a change in the top 10
	return ("▲" in results or "▼" in results or ":new:" in results)

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
	if message.guild.id == config.ps_server_id:
		return

	if message.content.startswith("!mainboard") or message.content.startswith("!starboard"):
		await handle_generic_leaderboard(message, "Starboard")
	elif message.content.startswith("!rainbow"):
		await handle_generic_leaderboard(message, "Rainbow")
	elif message.content.startswith("!arcade"):
		await handle_generic_leaderboard(message, "Arcade")
	elif message.content.startswith("!solution"):
		await handle_generic_leaderboard(message, "Solution")
	elif message.content.startswith("!challenge"):
		await handle_generic_leaderboard(message, "Challenge")
	elif message.content.startswith("!proof"):
		await handle_generic_leaderboard(message, "Proof")
	elif message.content.startswith("!video"):
		await handle_generic_leaderboard(message, "Video")
	elif message.content.startswith("!submitters"):
		await handle_submitters(message)
	elif message.content.startswith("!debug"):
		await debug(message)

#todo - genericise these
async def handle_generic_leaderboard(message, type):
	expected_prefix_length = len(type) + 2 #+2 because of the ! and the trailing space
	idx = 0 #default parameter
	if len(message.content) > expected_prefix_length:
		#if there was a parameter added and we can parse that
		expectedPrefix = "!"+type.lower()+" "
		idxParam = message.content.lower().lstrip(expectedPrefix)
		#for Starboard, also check for use of "mainboard"
		if type == "Starboard":
			idxParam.lstrip("!mainboard ") #doing this even if "Starboard" was used is fine
		#once we've stripped the command name, check that the parameter was valid
		if idxParam.isnumeric():
			#isnumeric excludes negatives or decimals, which is good for this use case
			idx = int(idxParam) - 1
	
	await scrape_leaderboard(type, True, idx, message.channel.id)

async def handle_submitters(message):
	days = 1 #default parameter
	if len(message.content) > 11:
		#if there was a parameter added and we can parse that
		daysParam = message.content.lstrip("!submitters ")
		if daysParam.isnumeric():
			#isnumeric excludes negatives or decimals, which is good for this use case
			days = int(daysParam)
		elif daysParam.startswith("all"):
			idx = 0 #default parameter
			if len(daysParam) > 4: #if the argument was e.g., "!submitters all 30"
				idxParam = daysParam.lstrip("all ")
				if idxParam.isnumeric():
					idx = int(idxParam) - 1
			await scrape_leaderboard("Submissions", True, idx, message.channel.id)
			return

	await top_submitters(days, message.channel.id)

async def debug(message):
	channel = client.get_channel(message.channel.id)
	if len(message.content) > 7:
		debugParam = message.content.lstrip("!debug ")
		if debugParam.startswith("roleping"):
			debugData = debugParam.lstrip("roleping")
			if "▲" in debugData or "▼" in debugData or ":new:" in debugData:
				await channel.send("<@&951246251427520512>")
			else:
				await channel.send("This would not have pinged a role")


client.run(TOKEN)