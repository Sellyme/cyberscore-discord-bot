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

firstLoad = True #check this on_ready() and then set it to false so we never duplicate the threads

@client.event
async def on_ready():
	global firstLoad
	print(client.user, "has connected to Discord!")
	
	if firstLoad:
		loop = asyncio.get_event_loop()
		loop.create_task(scrape_latest())
		loop.create_task(scrape_leaderboards())
		firstLoad = False

async def scrape_latest():
	cs_channel = client.get_channel(config.cs_submissions_channel)
	ps_channel = client.get_channel(config.ps_submissions_channel)
	cs_mod_channel = client.get_channel(config.cs_mod_channel)

	while True:
		results = scrape.scrape_latest()
		cs_results = results[0]
		ps_results = results[1]
		warn_results = results[2]

		#Messages to output to Cyberscore Discord
		for msg in cs_results:
			print(msg)
			
			#create embed for Discord
			embed = discord.Embed(description=msg)
			#this can often fail with a 504 HTTPException if Discord is having server issues
			#ideally we should add handling for this at some point and retry the message
			#as otherwise the message being sent just fails and is skipped
			await cs_channel.send(embed=embed)
		
		#Messages to output to Pokemon Snap Discord
		for msg in ps_results:
			#create embed for Discord
			embed = discord.Embed(description=msg)
			await ps_channel.send(embed=embed)
		
		#Messages to output to Cyberscore mod logs
		for msg in warn_results:
			#create embed for Discord
			embed = discord.Embed(description=msg)
			await cs_mod_channel.send(embed=embed)

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

			#if any of the important leaderboards have position changes, track them
			starboard_change = await scrape_leaderboard("Starboard")
			medal_change = await scrape_leaderboard("Medal")
			trophy_change = await scrape_leaderboard("Trophy")
			rainbow_change = await scrape_leaderboard("Rainbow")
			arcade_change = await scrape_leaderboard("Arcade")
			solution_change = await scrape_leaderboard("Solution")
			challenge_change = await scrape_leaderboard("Challenge")
			collection_change = await scrape_leaderboard("Collectible")
			incremental_change = await scrape_leaderboard("Incremental")
			speedrun_change = await scrape_leaderboard("Speedrun")
			proof_change = await scrape_leaderboard("Proof")
			video_change = await scrape_leaderboard("Video")
			
			top10_change = starboard_change or medal_change or trophy_change or rainbow_change or arcade_change or solution_change or challenge_change or collection_change or proof_change or video_change or speedrun_change

			#and then also run the remaining leaderboards
			await scrape_leaderboard("Level")
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
		

async def scrape_leaderboard(type, force = False, idx = 0, channel_id = config.leaderboard_channel, sortParam = 0):
	channel = client.get_channel(channel_id)

	results = scrape.scrape_leaderboard(type, force, idx, sortParam)
	#result should be a pure string
	print(results)
	if type == "Submissions" and not force:
		#this board isn't too useful to output daily since the 24hr submitters board exists
		return
	#add some more user-friendly names for the embed titles where needed
	elif type == "Video":
		name = "Video Proof"
	elif type == "Challenge":
		name = "User Challenge"
	elif type == "Medal":
		name = "Medal Table"
		if sortParam == 0:
			name += " <:plat:930611250809958501>"
		elif sortParam == 1:
			name += " <:gold:930611304727740487>"
		elif sortParam == 2:
			name += " <:silver:930611349267054702>"
		elif sortParam == 3:
			name += " <:bronze:930611393198190652>"
	elif type == "Trophy":
		name = "Trophy Table"
		if sortParam == 0:
			name += " (Points)"
		elif sortParam == 1:
			name += " (Platinum)"
		elif sortParam == 2:
			name += " (Gold)"
		elif sortParam == 3:
			name += " (Silver)"
		elif sortParam == 4:
			name += " (Bronze)"
		elif sortParam == 5:
			name += " (4ths)"
		elif sortParam == 6:
			name += " (5ths)"
	else:
		name = type

	#on the automated daily updates we already post the levels in the Incremental leaderboard
	#so if this was a daily update of the levels, DON'T make a Discord message
	if type != "Level" or force:
		#create embed for Discord
		embed = discord.Embed()
		embed.add_field(name=name, value=results)
		embed.timestamp = datetime.utcnow()
		await channel.send(embed=embed)

	#and indicate whether or not there was a change in the top 10
	return ("▲" in results or "▼" in results or ":new:" in results)

async def top_submitters(days = 1, idx = 0, channel_id = config.leaderboard_channel, type = "user"): #type = "user" or "game"
	channel = client.get_channel(channel_id)
	
	results = scrape.scrape_top_submitters(days, idx, type) #results is an array of [embed_body, range_string]
	embed_body = results[0]
	print(results[0])

	#generate embed header
	if type == "user":
		noun = "submitter"
	elif type == "game":
		noun = "game"

	if days == 1:
		fieldname = "Top " + noun + "s for today"
	else:
		fieldname = "Top " + noun + "s for the last " + str(days) + " days"
	
	#if there was a non-default idx set (e.g., not just looking at top 10 users) additionally print what range we're looking at
	if idx > 0:
		fieldname += " ("+results[1]+")"

	#create embed for Discord
	embed = discord.Embed()
	embed.add_field(name=fieldname, value=results[0])
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

	if message.content.startswith("!mainboard") or message.content.startswith("!starboard") or message.content.startswith("!csr"):
		await handle_generic_leaderboard(message, "Starboard")
	elif message.content.startswith("!medal"):
		await handle_generic_leaderboard(message, "Medal")
	elif message.content.startswith("!trophy"):
		await handle_generic_leaderboard(message, "Trophy")
	elif message.content.startswith("!rainbow") or message.content.startswith("!rp"):
		await handle_generic_leaderboard(message, "Rainbow")
	elif message.content.startswith("!arcade") or message.content.startswith("!tokens"):
		await handle_generic_leaderboard(message, "Arcade")
	elif message.content.startswith("!solution") or message.content.startswith("!bp"):
		await handle_generic_leaderboard(message, "Solution")
	elif message.content.startswith("!challenge") or message.content.startswith("!uc"):
		await handle_generic_leaderboard(message, "Challenge")
	elif message.content.startswith("!collect") or message.content.startswith("!stars"):
		await handle_generic_leaderboard(message, "Collectible")
	elif message.content.startswith("!incremental") or message.content.startswith("!xp") or message.content.startswith("!vxp"):
		await handle_generic_leaderboard(message, "Incremental")
	elif message.content.startswith("!level") or message.content.startswith("!cxp"):
		await handle_generic_leaderboard(message, "Level")
	elif message.content.startswith("!speedrun") or message.content.startswith("!time"):
		await handle_generic_leaderboard(message, "Speedrun")
	elif message.content.startswith("!proof"):
		await handle_generic_leaderboard(message, "Proof")
	elif message.content.startswith("!video") or message.content.startswith("!vp"):
		await handle_generic_leaderboard(message, "Video")
	elif message.content.startswith("!sub"):
		await handle_submitters(message, "user")
	elif message.content.startswith("!gamesub") or message.content.startswith("!gamessub"):
		await handle_submitters(message, "game")
	elif message.content.startswith("!debug"):
		await debug(message)

#todo - genericise these
async def handle_generic_leaderboard(message, type):
	print("Handling message: '" + message.content + "'")
	idx = 0 #default parameter
	sortParam = 0 #default parameter (plats for medal table, points for trophy table)
	args = get_args(message)

	if len(args) > 1:
		#if there was a parameter added and we can parse that
		idxParam = args[1]
		if idxParam.isnumeric():
			#isnumeric excludes negatives or decimals, which is good for this use case
			idx = int(idxParam) - 1
		
		#handle medal sort order params
		if type == "Medal":
			if "-g" in args:
				sortParam = 1
			elif "-s" in args:
				sortParam = 2
			elif "-b" in args:
				sortParam = 3
		elif type == "Trophy":
			if "-p" in args:
				sortParam = 1
			elif "-g" in args:
				sortParam = 2
			elif "-s" in args:
				sortParam = 3
			elif "-b" in args:
				sortParam = 4
			elif "-4" in args:
				sortParam = 5
			elif "-5" in args:
				sortParam = 6

	print("Scraping " + type + " leaderboard with idx " + str(idx) + " and sortParam " + str(sortParam)) 
	await scrape_leaderboard(type, True, idx, message.channel.id, sortParam)

async def handle_submitters(message, type): #type is either "user" or "game"
	days = 1 #default
	idx = 0 #default
	args = get_args(message)

	#if there was a parameter added we need to change the defaults
	if len(args) > 1:
		#first potential parameter is the number of days we want (e.g., "!subs 7" shows top submitters in the last week)
		daysParam = args[1]
		
		#if there was a second parameter added, use that as where to look on the leaderboard
		#e.g. "!subs ytd 20" shows positions 20-29 for most subs year-to-date
		if len(args) > 2:
			idxParam = args[2]
			if idxParam.isnumeric():
				idx = int(idxParam) - 1

		if daysParam.isnumeric():
			#isnumeric excludes negatives or decimals, which is good for this use case
			days = int(daysParam)
		elif daysParam == "ytd":
			#year-to-date stats, so get the current day of year index
			days = int(format(datetime.utcnow(), '%j'))
		elif daysParam == "all":
			if type == "game":
				await report_error(message.channel.id, "'All' search is not currently supported for game submissions")
				return
			print("Scraping Submissions leaderboard with idx " + str(idx))
			await scrape_leaderboard("Submissions", True, idx, message.channel.id)
			return
		#we ostensibly support daysParam being "today", e.g., "!subs today 15" to get today's leaderboard starting at 15th
		#but we don't actually need to code anything to support this, since falling through to the default case works fine

	print("Scraping top submitters for " + str(days) + " days with idx " + str(idx))
	await top_submitters(days, idx, message.channel.id, type)

def get_args(message):
	args = message.content.split(" ")
	#remove any empty strings from the args, so "!starboard  20" still works despite two spaces
	args = list(filter(None, args))
	return args

async def debug(message):
	channel = client.get_channel(message.channel.id)
	if len(message.content) > 7:
		debugParam = message.content.lstrip("!debug ")
		if debugParam.startswith("forcedaily "):
			forceParam = debugParam.lstrip("forcedaily ")
			await scrape_leaderboard(forceParam)

async def report_error(channel_id, message):
	channel = client.get_channel(channel_id)
	await channel.send(message)

client.run(TOKEN)