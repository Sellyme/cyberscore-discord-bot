import os #reading auth file
import discord #discord bot
from dotenv import load_dotenv #discord auth
from datetime import datetime, timedelta
import asyncio #allow multiple threads
import inflect #used for converting integers to ordinal positions
import re
import traceback

import scrape, config, pokemon #custom imports

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()
infeng = inflect.engine()

firstLoad = True #check this on_ready() and then set it to false so we never duplicate the threads

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

			#Messages to output to Cyberscore #pokémon channel
			for msg in size_results:
				embed = discord.Embed(description=msg)
				await cs_pokemon_channel.send(embed=embed)
		except Exception as e:
			traceback.print_exc()
			print("Exception occurred in latest subs scrape")
		finally:
			await asyncio.sleep(config.submissions_frequency)

async def scrape_leaderboards():
	while True:
		try:
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
		except Exception as e:
			print(e)
			print("Exception occurred in leaderboards scrape")
		finally:
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


async def profile_stats(message):
	channel = client.get_channel(message.channel.id)

	args = get_args(message)

	if len(args) <= 1:
		await report_error(message.channel.id, "Can not load profile without a username or user ID. Try e.g., `!profile Sellyme`")
		return
	else:
		#"username" is a misnomer - it has to be a user ID for now
		#but names will be accepted once the updated API is live, and this feature won't be public before then
		username = args[1]

	sub_milestones = [25,50,100,250,500,1000,2500,5000,10000,25000,50000,100000]
	leadership_awards = [100,10,3,2,1]
	user_data = scrape.scrape_profile(username)

	#fail if user wasn't found
	if user_data == None:
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
					field_text += "**"+board.capitalize() + "**: " + infeng.ordinal(position) + "\n"
				else:
					field_text += "**"+board.capitalize() + "**: N/A\n"
		else:
			continue #this data is VERY unreliable right now, remove this line when API is more robust
			for board in user_data[key]:
				score = user_data[key][board]
				field_text += "**"+board.capitalize() + "**: " + str(score)
				#find the next medal up
				max_milestone = sub_milestones[len(sub_milestones)-1]
				for target in sub_milestones:
					if score < target: #we've found the first milestone the user hasn't reached:
						max_milestone = target
						break
					#and if we loop through every milestone and the score isn't lower than any of them
					#we fall through to the default (which is the final milestone in the list)
				field_text += "/" + str(max_milestone) + "\n"
		embed.add_field(name=field_name, value=field_text, inline=True)

	user_avatar = "https://cyberscore.me.uk/userpics/" + str(user_data["user_id"]) + ".jpg"
	embed.set_author(name=user_data['username'], icon_url=user_avatar)

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
	elif message.content.startswith("!challenge") or message.content.startswith("!uc") or message.content.startswith("!sp ") or message.content == "!sp":
		await handle_generic_leaderboard(message, "Challenge")
	elif message.content.startswith("!collect") or message.content.startswith("!stars") or message.content.startswith("!cyberstar"):
		await handle_generic_leaderboard(message, "Collectible")
	elif message.content.startswith("!incremental") or message.content.startswith("!xp") or message.content.startswith("!vxp"):
		await handle_generic_leaderboard(message, "Incremental")
	elif message.content.startswith("!level") or message.content.startswith("!cxp"):
		await handle_generic_leaderboard(message, "Level")
	elif message.content.startswith("!speedrun") or message.content.startswith("!time") or message.content.startswith("!sr"):
		await handle_generic_leaderboard(message, "Speedrun")
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
	elif message.content.startswith("!profile"):
		await profile_stats(message)
	elif message.content.startswith("!forms"):
		await get_pokemon_forms(message)
	elif message.content.startswith("!dex "):
		await get_pokemon_dex(message)
	elif message.content.startswith("!height "):
		await compare_height(message)
	elif message.content.startswith("!weight "):
		await compare_weight(message)

async def handle_generic_leaderboard(message, type):
	print("Handling message: '" + message.content + "'")
	idx = 0 #default parameter
	sortParam = 0 #default parameter (plats for medal table, points for trophy table)
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
				break
		
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

async def get_pokemon_forms(message):
	mon = message.content.removeprefix("!forms").strip()
	if not mon:
		report_error(message.channel.id, "Must supply a dex number or Pokemon name to search for")
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
		report_error(message.channel.id, "You must supply both a dex item to look up, and a Pokémon form name to search for. Use `!forms {dex_number}` to see valid form names for a certain species.")
		return
	
	if params.startswith("type"):
		mon = pokemon.format_name(params.removeprefix("type").strip())
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
		height = pokemon.get_dex_height(mon)
		output = str(height)+" m" if height else height
	else:
		await report_error(message.channel.id, "Cannot understand parameters given. Please enter first the dex field you are requesting and then the Pokemon name, e.g., `!dex type Pidgey`")

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
	
	size_str = "larger" if result[0] > 0 else "smaller"
	output = "Chance of a " + m.group(1).title() + " " + size_str + " than " + m.group(2) + " m:\n"
	win_chances = result[1]
	
	if len(win_chances) == 1 or round(win_chances[0],5) == round(win_chances[1],5) == round(win_chances[2],5):
		if win_chances[0] > 0:
			output += f"{win_chances[0]:.3%}"
		else:
			output = "A " + m.group(1).title() + " " + size_str + " than " + m.group(2) +" m is not possible."
	else:
		output += "Class 1: "
		output += f"{win_chances[0]:.3%}" if win_chances[0] > 0 else "Not Possible"
		output += "\nClass 2: "
		output += f"{win_chances[1]:.3%}" if win_chances[1] > 0 else "Not Possible"
		output += "\nClass 3: "
		output += f"{win_chances[2]:.3%}" if win_chances[2] > 0 else "Not Possible"
	
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
	win_chances = result[1]
	print("win_chances", win_chances)

	#print(win_chances)
	if round(win_chances[0],5) == round(win_chances[1],5) == round(win_chances[2],5):
		if win_chances[0] > 0:
			output += f"{win_chances[0]:.3%}"
		else:
			output = "A " + m.group(1).title() + " " + size_str + " than " + m.group(2) +" kg is not possible."
	else:
		output += "Class 1: "
		output += f"{win_chances[0]:.3%}" if win_chances[0] > 0 else "Not Possible"
		output += "\nClass 2: "
		output += f"{win_chances[1]:.3%}" if win_chances[1] > 0 else "Not Possible"
		output += "\nClass 3: "
		output += f"{win_chances[2]:.3%}" if win_chances[2] > 0 else "Not Possible"
	
	await message.channel.send(output)
	

def get_args(message):
	args = message.content.split(" ")
	#remove any empty strings from the args, so "!starboard  20" still works despite two spaces
	args = list(filter(None, args))
	return args

async def debug(message):
	if len(message.content) > 7:
		debugParam = message.content.removeprefix("!debug ")
		if debugParam.startswith("forcedaily "):
			forceParam = debugParam.removeprefix("forcedaily ")
			await scrape_leaderboard(forceParam)



async def report_error(channel_id, message):
	channel = client.get_channel(channel_id)
	await channel.send(message)

client.run(TOKEN)