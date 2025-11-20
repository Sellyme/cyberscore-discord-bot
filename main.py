import os #reading auth file
import sys #needed to test if we're in IDLE
import discord #discord bot
from dotenv import load_dotenv #discord auth
from datetime import datetime, timedelta, timezone
import asyncio #allow multiple threads
import inflect #used for converting integers to ordinal positions
import re, math
import traceback
import signal
import sentry_sdk

import scrape, config, pokemon, graph, cmfn #custom imports

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
inflect_engine = inflect.engine()

firstLoad = True #check this on_ready() and then set it to false so we never duplicate the threads

sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"))

@client.event
async def on_ready():
	global firstLoad

	print(client.user, "has connected to Discord!")

	if firstLoad:
		loop = asyncio.get_event_loop()
		loop.create_task(scrape_latest())
		loop.create_task(scrape_leaderboards())
		pokemon.get_game_master()
		firstLoad = False

async def scrape_latest():
	cs_channel = client.get_channel(config.cs_submissions_channel)
	ps_channel = client.get_channel(config.ps_submissions_channel)
	cs_mod_channel = client.get_channel(config.cs_mod_channel)
	cs_pokemon_channel = client.get_channel(config.cs_pokemon_channel)

	while True:
		try:
			results = scrape.scrape_latest()
			cs_results = results[0]
			ps_results = results[1]
			warn_results = results[2]
			size_results = results[3]

			#Messages to output to Cyberscore Discord
			for msg in cs_results:
				print(msg)

				#create embed for Discord
				embed = discord.Embed(description=msg)
				#this can often fail with a 504 HTTPException if Discord is having server issues
				#ideally we should add handling for this at some point and retry the message
				#as otherwise the message being sent just fails and is skipped
				await cs_channel.send(embed=embed)

			#Messages to output to Pokémon Snap Discord
			for msg in ps_results:
				#create embed for Discord
				embed = discord.Embed(description=msg)
				await ps_channel.send(embed=embed)

			#Messages to output to Cyberscore mod logs
			for msg in warn_results:
				#create embed for Discord
				embed = discord.Embed(description=msg)
				await cs_mod_channel.send(embed=embed)

			#Messages to output to Cyberscore #pokémon channel
			for msg in size_results:
				embed = discord.Embed(description=msg)
				await cs_pokemon_channel.send(embed=embed)
		except Exception as e:
			traceback.print_exc()
			sentry_sdk.capture_exception(e)
			print("Exception occurred in latest subs scrape")
		finally:
			await asyncio.sleep(config.submissions_frequency)

async def scrape_leaderboards():
	while True:
		try:
			f = open("data/last_leaderboards", "r+")
			last_scrape = f.read().strip()
			last_scrape_dt = datetime.strptime(last_scrape, "%Y-%m-%d %H:%M:%S")
			last_scrape_dt = last_scrape_dt.replace(tzinfo=timezone.utc) #force a timezone-aware datetime
			lock_scrape = last_scrape_dt + timedelta(0.1)
			next_scrape = last_scrape_dt + timedelta(1)

			print("Checking leaderboard scrape")
			#we want the leaderboard scrape to only run around midnight UTC, so init a datetime
			now = datetime.now(timezone.utc)
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
				#speedrun_change = await scrape_leaderboard("Speedrun")
				proof_change = await scrape_leaderboard("Proof")
				video_change = await scrape_leaderboard("Video")

				top10_change = starboard_change or medal_change or trophy_change or rainbow_change or arcade_change \
							   or solution_change or challenge_change or collection_change or proof_change \
							   or video_change or incremental_change

				#and then also run the remaining leaderboards
				await scrape_leaderboard("Level")
				await scrape_leaderboard("Submissions")
				await top_submitters(1)

				#save the most recent scrape
				f.seek(0)
				f.write(now.strftime("%Y-%m-%d %H:%M:%S"))
				f.truncate()

				channel = client.get_channel(config.leaderboard_channel)

				#if there was a cc, print that
				if now.day == 1:
					month = now.month - 1
					year = now.year
					if month == 0:
						month = 12
						year = year-1
					cc_url = str(year) + "-" + str(month)
					await print_chart_challenge(0, cc_url, channel)

				#finally, print out a role ping if there was a positional change
				if top10_change:
					channel = client.get_channel(config.leaderboard_channel)
					await channel.send("<@&951246251427520512>")

			f.close()
		except Exception as e:
			print(e)
			print("Exception occurred in leaderboards scrape")
			sentry_sdk.capture_exception(e)
		finally:
			#and re-check hourly
			await asyncio.sleep(config.leaderboard_frequency)


#async def scrape_level_changes():
#	channel = config.

async def scrape_leaderboard(board_type, force = False, idx = 0, channel_id = config.leaderboard_channel,
							 sort_param = 0, ytd = False, gain = False):
	#PARAMS:
	#board_type - the leaderboard size_type to scrape, e.g., "arcade"
	#force - whether to force an update to #leaderboards, used only for manually fixing errors
	#idx - the position at which to start displaying the board, to view further down than top 10
	#channel_id - if called by a user command, the channel in which that command was sent
	#sort_param - for boards with multiple sorts (e.g., Medal Table), what sort order is desired
	#ytd - if true, show gains over the current calendar year, instead of the current calendar day. TODO - extend this to accept integer numbers of days in addition to the simple keyword
	#gain - if true, order the results by gains in the relevant period rather than ordering by current totals

	channel = client.get_channel(channel_id)

	results = scrape.scrape_leaderboard(board_type, force, idx, sort_param, ytd, gain)
	#result should be a pure string
	print(results)
	if board_type == "Medal":
		name = "Medal Table"
		if sort_param == 0:
			name += " <:plat:930611250809958501>"
		elif sort_param == 1:
			name += " <:gold:930611304727740487>"
		elif sort_param == 2:
			name += " <:silver:930611349267054702>"
		elif sort_param == 3:
			name += " <:bronze:930611393198190652>"
	elif board_type == "Trophy":
		name = "Trophy Table"
		if sort_param == 0:
			name += " (Points)"
		elif sort_param == 1:
			name += " (Platinum)"
		elif sort_param == 2:
			name += " (Gold)"
		elif sort_param == 3:
			name += " (Silver)"
		elif sort_param == 4:
			name += " (Bronze)"
		elif sort_param == 5:
			name += " (4ths)"
		elif sort_param == 6:
			name += " (5ths)"
	else:
		name = cmfn.get_scoreboard_names(board_type, sort_param)['display_name']

	#level leaderboard is effectively printed in the VXP leaderboard
	#and submissions leaderboard changes are shown in daily top subs
	#so we don't print those two leaderboards by default.
	if (board_type != "Level" and board_type != "Submissions") or force:
		#create embed for Discord
		embed = discord.Embed()
		embed.add_field(name=name, value=results)
		embed.timestamp = datetime.now(timezone.utc)
		await channel.send(embed=embed)

	#and indicate whether there was a change in the top 10
	return "▲" in results or "▼" in results or ":new:" in results

async def top_submitters(days = 1, idx = 0, channel_id = config.leaderboard_channel, board_type ="user"):
	#board_type = "user" or "game"
	channel = client.get_channel(channel_id)

	results = scrape.scrape_top_submitters(days, idx, board_type) #results is an array of [embed_body, range_string]
	embed_body = results[0]
	print(results[0])

	#generate embed header
	if board_type == "user":
		noun = "submitter"
	elif board_type == "game":
		noun = "game"
	else:
		return await report_error(channel_id, "Board size_type " + str(board_type) + " invalid")

	if days == 1:
		field_name = "Top " + noun + "s for today"
	else:
		field_name = "Top " + noun + "s for the last " + str(days) + " days"

	#if there was a non-default idx set (e.g., not just looking at top 10 users) additionally print what range
	#we're looking at
	if idx > 0:
		field_name += " ("+results[1]+")"

	#create embed for Discord
	embed = discord.Embed()
	embed.add_field(name=field_name, value=embed_body)
	embed.timestamp = datetime.now(timezone.utc)
	await channel.send(embed=embed)

async def profile_stats(message):
	channel = client.get_channel(message.channel.id)

	args = get_args(message)

	if len(args) <= 1:
		await report_error(message.channel.id, "Can not load profile without a username or user ID. Try e.g., `!profile Sellyme`")
		return
	else:
		username = args[1]

	#sub_milestones = [25,50,100,250,500,1000,2500,5000,10000,25000,50000,100000]
	#leadership_awards = [100,10,3,2,1]
	user_data = scrape.scrape_profile(username)

	#fail if user wasn't found
	if user_data is None:
		await report_error(message.channel.id, "Can not find profile with username/user_id `"+username+"`")
		return

	embed = discord.Embed()

	for key in user_data:
		field_name = key.capitalize()
		field_text = ""
		if key == "username" or key == "user_id":
			continue
		elif key == "positions":
			for board in user_data[key]:
				position = user_data[key][board]
				if board == "average":
					field_text += "**"+board.capitalize() + "**: #" + position + "\n"
				elif position:
					field_text += "**" + board.capitalize() + "**: " + inflect_engine.ordinal(position) + "\n"
				else:
					field_text += "**"+board.capitalize() + "**: N/A\n"
		else:
			continue #this data is VERY unreliable right now, remove this line when API is more robust
			# for board in user_data[key]:
			# 	score = user_data[key][board]
			# 	field_text += "**"+board.capitalize() + "**: " + str(score)
			# 	#find the next medal up
			# 	max_milestone = sub_milestones[len(sub_milestones)-1]
			# 	for target in sub_milestones:
			# 		if score < target: #we've found the first milestone the user hasn't reached:
			# 			max_milestone = target
			# 			break
			# 		#and if we loop through every milestone and the score isn't lower than any of them
			# 		#we fall through to the default (which is the final milestone in the list)
			# 	field_text += "/" + str(max_milestone) + "\n"

		embed.add_field(name=field_name, value=field_text, inline=True)

	user_avatar = "https://cyberscore.me.uk/userpics/" + str(user_data["user_id"]) + ".jpg"
	embed.set_author(name=user_data['username'], icon_url=user_avatar)

	embed.timestamp = datetime.now(timezone.utc)
	await channel.send(embed=embed)

@client.event
async def on_message(message):
	#ignore messages from bots to avoid double-posting on PluralKit etc.
	if message.author.bot:
		return

	#if the message is a DM, don't attempt to do anything and forward the message to me
	if isinstance(message.channel, discord.DMChannel):
		me = await client.fetch_user(101709643822157824)
		await me.send(f"Sellybot DM from {message.author}:\n{message.content}")
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
	elif message.content.startswith("!challenge") or message.content.startswith("!uc") or message.content.startswith("!sp ") or message.content == "!sp":
		await handle_generic_leaderboard(message, "Challenge")
	elif message.content.startswith("!collect") or message.content.startswith("!stars") or message.content.startswith("!cyberstar"):
		await handle_generic_leaderboard(message, "Collectible")
	elif message.content.startswith("!incremental") or message.content.startswith("!xp") or message.content.startswith("!vxp"):
		await handle_generic_leaderboard(message, "Incremental")
	elif message.content.startswith("!level") or message.content.startswith("!cxp"):
		await handle_generic_leaderboard(message, "Level")
	elif message.content.startswith("!speedrun") or message.content.startswith("!time") or message.content.startswith("!sr"):
		#Speedrun is disabled
		await report_error(message.channel, "The speedrun leaderboard has been deprecated.")
	elif message.content.startswith("!proof"):
		await handle_generic_leaderboard(message, "Proof")
	elif message.content.startswith("!vid") or message.content.startswith("!vp"):
		await handle_generic_leaderboard(message, "Video")
	elif message.content.startswith("!sub"):
		await handle_submitters(message, "user")
	elif message.content.startswith("!gamesub") or message.content.startswith("!gamessub"):
		await handle_submitters(message, "game")
	elif message.content.startswith("!debug"):
		await debug(message)
	elif message.content.startswith("!profile") or message.content.startswith("!user"):
		await profile_stats(message)
	elif message.content.startswith("!forms"):
		await get_pokemon_forms(message)
	elif message.content.startswith("!dex "):
		await get_pokemon_dex(message)
	elif message.content.startswith("!height "):
		await compare_height(message)
	elif message.content.startswith("!weight "):
		await compare_weight(message)
	elif message.content.startswith("!chartchallenge") or message.content.startswith("!cc"):
		await handle_chart_challenge(message)
	elif message.content.startswith("!lead"):
		await handle_lead_graph(message)
	elif message.content.startswith("!ugraph"):
		await handle_user_graph(message)

async def handle_generic_leaderboard(message, board_type):
	print("Handling message: '" + message.content + "'")
	idx = 0 #default parameter
	sortParam = 0 #default parameter (plats for medal table, points for trophy table)
	ytd = False
	gain = False
	args = get_args(message)

	if len(args) > 1:
		#if there was a parameter added, search through to see if there's a numeric parameter to indicate index
		for param in args:
			if param.isnumeric():
				#isnumeric excludes negatives or decimals, which is good for this use case
				idx = int(param) - 1
				if idx > 90:
					await report_error(message.channel.id, "Only the top 100 for each leaderboard are tracked.")
					#non-fatal error, just print the bottom ten
			elif param == "ytd":
				#if the string "ytd" is present, toggle the ytd flag
				ytd = True
			elif param == "gain":
				gain = True

		#handle medal/trophy sort order params
		sortParam = cmfn.get_sort_param(board_type, args)

	print("Scraping " + board_type + " leaderboard with idx " + str(idx) + " and sort_param " + str(sortParam))
	await scrape_leaderboard(board_type, True, idx, message.channel.id, sortParam, ytd, gain)

async def handle_submitters(message, board_type): #board_type is either "user" or "game"
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
		elif daysParam.lower() == "ytd":
			#year-to-date stats, so get the current day of year index
			days = int(format(datetime.now(timezone.utc), '%j'))
		elif daysParam.lower() == "all":
			if board_type == "game":
				await report_error(message.channel.id, "'All' search is not currently supported for game submissions")
				return
			print("Scraping Submissions leaderboard with idx " + str(idx))
			await scrape_leaderboard("Submissions", True, idx, message.channel.id)
			return
		#we ostensibly support daysParam being "today", e.g., "!subs today 15" to get today's leaderboard starting at 15th,
		#but we don't actually need to code anything to support this, since falling through to the default case works fine

	print("Scraping top submitters for " + str(days) + " days with idx " + str(idx))
	await top_submitters(days, idx, message.channel.id, board_type)

async def handle_chart_challenge(message):
	print("Handling message: '" + message.content + "'")
	idx = 0 #default parameter
	month = "now" #default parameter
	args = get_args(message)

	if len(args) > 1:
		for param in args:
			if param.isnumeric():
				#months aren't represented numerically, so this must represent the desired index
				idx = int(param) - 1
				#no error message on high indices because the size of the board varies monthly and rarely hits 100 anyway
			elif param != "!cc":
				month = param

	#the site doesn't use a leading zero for months in the URL, so we need some handling for that
	if month == "now":
		# the '#' character in this string strips the leading zero
		#if porting to Unix, this needs to be replaced with a '-' like so: "%Y-%-m"
		month = datetime.now(timezone.utc).strftime("%Y-%#m")
	else:
		#if a user requests a month of the form 2024-03 we can easily convert it
		month = month.replace("-0","-")

	#and post to Discord
	channel = client.get_channel(message.channel.id)
	await print_chart_challenge(idx, month, channel)


async def print_chart_challenge(idx, month, channel):
	print("Scraping chart challenge leaderboard with idx " + str(idx) + " and month " + month)
	results = await scrape.scrape_chart_challenge(idx, month)
	embed_name = "Chart Challenge (" + month + ")"

	embed = discord.Embed()
	embed.add_field(name=embed_name, value=results)
	embed.timestamp = datetime.now(timezone.utc)
	await channel.send(embed=embed)

async def get_pokemon_forms(message):
	mon = message.content.removeprefix("!forms").strip()
	if not mon:
		await report_error(message.channel.id, "Must supply a dex number or Pokemon name to search for")
		return

	if mon.isnumeric():
		#IDs need leading zeroes padded to 4 digits, e.g., "0001" in #0001 - Bulbasaur 
		key = ("000"+mon)[-4:]
		forms = pokemon.get_forms(key, "number")
		reply = "Pokedex forms found for #" + key + ":\n"
	else:
		key = pokemon.format_name(mon)
		forms = pokemon.get_forms(key, "name")
		reply = "Pokedex forms found for " + key + ":\n"

	if not forms:
		await report_error(message.channel.id, "Pokemon '" + key + "' could not be found")
		return

	for form in forms:
		reply += form.removesuffix("_NORMAL")+"\n"
	await message.channel.send(reply)

async def get_pokemon_dex(message):
	params = message.content.removeprefix("!dex").strip()
	if not params or " " not in params:
		await report_error(message.channel.id, "You must supply both a dex item to look up, and a Pokémon form name to search for. Use `!forms {dex_number}` to see valid form names for a certain species.")
		return

	if params.startswith("size_type"):
		mon = pokemon.format_name(params.removeprefix("size_type").strip())
		output = pokemon.get_type(mon)
	elif params.startswith("bcr"):
		mon = pokemon.format_name(params.removeprefix("bcr").strip())
		output = pokemon.get_bcr(mon)
	elif params.startswith("stats"):
		mon = pokemon.format_name(params.removeprefix("stats").strip())
		output = pokemon.get_stats(mon)
	elif params.startswith("moves"):
		mon = pokemon.format_name(params.removeprefix("moves").strip())
		output = pokemon.get_moves(mon)
	elif params.startswith("weight"):
		mon = pokemon.format_name(params.removeprefix("weight").strip())
		weight = pokemon.get_dex_weight(mon)
		output = str(weight)+" kg" if weight else weight
	elif params.startswith("height"):
		mon = pokemon.format_name(params.removeprefix("height").strip())
		output = pokemon.get_bounds(mon)
	else:
		return await report_error(message.channel.id, "Cannot understand parameters given. Please enter first the dex field you are requesting and then the Pokemon name, e.g., `!dex size_type Pidgey`")

	if output:
		await message.channel.send(output)
	else:
		await report_error(message.channel.id, "Pokemon '" + mon + "' could not be found")

async def compare_height(message):
	params = message.content.removeprefix("!height").strip()
	param_regex = r'(.*) (\d+(.\d+)?) ?m?'
	m = re.fullmatch(param_regex, params)
	if not m:
		await report_error(message.channel.id, "Could not find a Pokemon name and height in your message. Please include both in that order, e.g., `!height Blastoise 1.74`")
		return

	mon = pokemon.format_name(m.group(1))
	result = pokemon.get_height_chance(mon, float(m.group(2)))
	if not result:
		await report_error(message.channel.id, "Pokemon "+m.group(1)+" could not be matched to any game master entry. Try searching for form names by dex number to see what valid names there are, e.g., `!forms 20` for Raticate")
		return

	#get correct article
	if m.group(1).title()[0] in "AEIOU":
		a_an = "n"
	else:
		a_an = ""

	size_str = "larger" if result[0] > 0 else "smaller"
	output = "Chance of a"+a_an+" " + m.group(1).title() + " " + size_str + " than " + m.group(2) + " m:\n"
	win_chance = result[1]

	if win_chance > 0:
		frac = round(1/win_chance)
		size = max(3,round(math.log(frac,10))-1) #this will show e.g., 5 decimals for a 1 in 1mil chance
		perc = str(round(win_chance * 100,size))
		output += perc+"% (1 in "+str(frac)+")"
	else:
		output = "A"+a_an+" " + m.group(1).title() + " " + size_str + " than " + m.group(2) +" m is not possible."

	await message.channel.send(output)

async def compare_weight(message):
	params = message.content.removeprefix("!weight").strip()
	param_regex = r'(.*) (\d+(.\d+)?) ?k?g?'
	m = re.fullmatch(param_regex, params)
	if not m:
		await report_error(message.channel.id, "Could not find a Pokemon name and height in your message. Please include both in that order, e.g., `!weight Butterfree 51.97`")
		return

	mon = pokemon.format_name(m.group(1))
	result = pokemon.get_weight_chance(mon, float(m.group(2)))
	if not result:
		await report_error(message.channel.id, "Pokemon "+m.group(1)+" could not be matched to any game master entry. Try searching for form names by dex number to see what valid names there are, e.g., `!forms 20` for Raticate")

	size_str = "heavier" if result[0] > 0 else "lighter"
	output = "Chance of a " + m.group(1).title() + " " + size_str + " than " + m.group(2) + " kg:\n"
	win_chance = result[1]
	print("win_chance", win_chance)

	#print(win_chance)
	if win_chance > 0:
		frac = round(1/win_chance)
		size = max(3,round(math.log(frac,10))-1) #this will show e.g., 5 decimals for a 1 in 1mil chance
		perc = str(round(win_chance * 100,size))
		output += perc+"% (1 in "+str(frac)+")"
	else:
		output = "A " + m.group(1).title() + " " + size_str + " than " + m.group(2) +" kg is not possible."

	await message.channel.send(output)

async def handle_lead_graph(message):
	args = get_args(message)
	board_type = args[1]
	sort_type = cmfn.get_sort_param(board_type, args)
	graph_name = graph.generate_lead_diff_graph(board_type, sort_type)

	channel = client.get_channel(message.channel.id)
	#create the discord File
	with open("data/graphs/"+graph_name, 'rb') as f:
		picture = discord.File(f)
		await channel.send(file=picture)

	try:
		os.remove("data/graphs/"+graph_name)
	except Exception as e:
		sentry_sdk.capture_exception(e)
		print("Error removing graph", graph_name)

async def handle_user_graph(message):
	args = get_args(message)
	user = args[1]
	board_type = args[2]
	sort_type = cmfn.get_sort_param(board_type, args)
	graph_name = graph.generate_user_graph(user, board_type, sort_type)

	channel = client.get_channel(message.channel.id)
	# create the discord File
	with open("data/graphs/" + graph_name, 'rb') as f:
		picture = discord.File(f)
		await channel.send(file=picture)

	try:
		os.remove("data/graphs/" + graph_name)
	except Exception as e:
		sentry_sdk.capture_exception(e)
		print("Error removing graph", graph_name)

def get_args(message):
	args = message.content.split(" ")
	#remove any empty strings from the args, so "!starboard  20" still works despite two spaces
	args = list(filter(None, args))
	return args

async def debug(message):
	if len(message.content) > 7:
		debugParam = message.content.removeprefix("!debug ")
		if debugParam.lower().startswith("forcedaily "):
			forceParam = debugParam.removeprefix("forcedaily ")
			await scrape_leaderboard(forceParam)
		if debugParam.lower().startswith("ping"):
			await direct_output(message.channel.id, "pong")
		elif debugParam.lower() == "syn":
			await direct_output(message.channel.id, "ACK")


async def report_error(channel_id, message):
	channel = client.get_channel(channel_id)
	await channel.send(message)

#report_error is a good name for actual error reporting but sometimes we want
#to do exactly the same thing but without implying it's an error
async def direct_output(channel_id, message):
	await report_error(channel_id, message)

#allow running the bot in IDLE or PyCharm for testing/utility funcs without actually connecting to Discord
if 'idlelib.run' not in sys.modules and "PYCHARM_HOSTED" not in os.environ:
	def sigterm(signum, frame):
		exit(0)

	signal.signal(signal.SIGTERM, sigterm)
	client.run(TOKEN)
else:
	pokemon.get_game_master()
	def chevo(x,y,z,a=False):
		pokemon.check_evo_chances(x,y,z,a)
	def bound(x):
		pokemon.get_bounds(x)
