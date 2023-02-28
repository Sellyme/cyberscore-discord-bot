import requests, re, math, json
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import cmfn #common functions

CS_PREFIX = "https://cyberscore.me.uk"

def scrape_latest():
	URL = CS_PREFIX + "/latest-submissions"
	cs_results = [] #messages to output to Cyberscore Discord
	ps_results = [] #messages to output to New Pokemon Snap Discord
	warn_results = [] #messages to output to a staff channel on certain keywords
	#any of these keywords occurring in a comment should have the record checked for validity
	warn_keywords = ["emu", "emulator", "emulation", "emulated", "rom", "vba", "dolphin", "desmume", "retroarch", "p64", "swanstation", "mesen", "snes9x", "zsnes", "mgba", "libretro", "retropie", "melonds", "mame", "z64", "iso", "stella", "ppsspp", "epsxe", "gliden", "jabo"]

	#perform web scrape
	page = requests.get(URL)
	soup = BeautifulSoup(page.content, "html.parser")
	
	#load in the last update time
	f = open("last_update", "r+")
	last_update = f.read()
	new_update = "0"
	
	table = soup.find(id="latest_records_table")
	#delete the header row
	table.select_one("tr").decompose()
	records = table.find_all("tr")
	#and reverse them so we check the oldest first
	records.reverse()
	
	#there's a bug in CS where updated scores are incorrectly displayed on latest-submissions
	#as being in the position the old score was before the update. This only occurs
	#for a very short time window after the score was published.
	#To avoid this from occuring, we get the current UTC time, and then ignore any scores
	#that were published within the last few seconds, and only record them on the next scrape
	maximum_datetime = datetime.utcnow() - timedelta(seconds=3)
	maximum_datetime_str = maximum_datetime.strftime("%Y-%m-%d %H:%M:%S")

	#iterate over all records
	for record in records:
		columns = list(record.find_all("td"))
		#skip any records we've already scanned
		date = columns[9].get_text()
		if date <= last_update:
			#print ("Skipping update on", date, "as it is before", last_update)
			continue
		elif date > maximum_datetime_str:
			print("Skipping update on", date, "as it exceeds max DT", maximum_datetime_str)
			continue
		else:
			new_update = date

		flag_col = columns[0]
		name_col = columns[1]
		game_col = columns[2]
		chart_col = columns[3]
		score_col = columns[4]
		medal_col = columns[5]
		pos_col = columns[6]
		type_col = columns[7]
		award_col = columns[8]

		country = flag_col.img.get('alt').lower()
		flag_emoji = cmfn.get_flag_emoji(country)
		
		user_name = name_col.a.get_text().strip()
		user_link = name_col.a['href']
		user = "["+user_name+"]("+user_link+")"
		
		game_name = game_col.strong.get_text().strip()
		game_link = game_col.a['href']
		game = "["+game_name+"]("+CS_PREFIX+game_link+")"
		
		chart_links = list(chart_col.find_all('a'))
		#group names don't exist for all charts, so we need to check chart_links length
		#and only construct group name if > 1
		if(len(chart_links) > 1):
			group_name = chart_links[0].get_text().strip()
			chart_name = chart_links[1].get_text().strip()
			chart_link = chart_col.find_all('a')[1]['href']
			chart = "["+group_name + " → " + chart_name+"]("+CS_PREFIX+chart_link+")"
		else:
			chart_name = chart_links[0].get_text().strip()
			chart_link = chart_col.a['href']
			chart = "["+chart_name+"]("+CS_PREFIX+chart_link+")"
		
		score_value = score_col.a.get_text()
		score_link = score_col.a['href']
		score = "["+score_value+"]("+CS_PREFIX+score_link+")"

		if score_col.img:
			#this is only mildly sanitised, so users can break visual formatting
			#(e.g., underlines, bold, italics, strikethrough)
			#but escaping the embed should not be possible
			comment = "\n*"+score_col.img['title']+"*"
		else:
			comment = ""
		
		if medal_col.img:
			medal_name = medal_col.img['title']
			if medal_name == "Platinum":
				medal = " <:plat:930611250809958501>"
			elif medal_name == "Gold":
				medal = " <:gold:930611304727740487>"
			elif medal_name == "Silver":
				medal = " <:silver:930611349267054702>"
			elif medal_name == "Bronze":
				medal = " <:bronze:930611393198190652>"
			else:
				medal = ""
		else:
			medal = ""
		
		pos = pos_col.get_text().replace(" ","").strip()
		csr = award_col.strong
		#csr is not displayed for UC charts, so display Challenge Points instead
		#for unranked charts (e.g., time played incrementals) display nothing)
		if csr:
			csr = csr.get_text().strip()
		elif award_col.span:
			csr = award_col.span.get_text().strip()
		else:
			csr = ""

		#construct string
		output = flag_emoji + " " + user + " just scored " + score
		output += " (Pos: **" + pos + "**" + medal
		#add CSR/UC if applicable
		if csr:
			output += " · " + csr
		output += ")\n"
		output += game + " → " + chart
		output += comment #if the comment exists it will appear italicised on a new line
		
		cs_results.append(output)
		#if this is for New Pokemon Snap, output to that as well
		if game_link == "/game/2785":
			ps_results.append(output)
		
		#we need to check the comment for any instance of certain words
		#to avoid having to account for punctuation, strip everything that isn't a-z or whitespace
		comment_stripped = re.sub(r'[^a-z ]+', '', comment.lower())
		comment_array = comment_stripped.split(" ") #and split all the words into components
		#check if the logical AND of the two word sets contains any elements
		comment_flag = bool(set(comment_array) & set(warn_keywords))
		if comment_flag:
			warn_results.append(output)


	#once we've iterated over everything we can save the last update date
	if new_update > last_update:
		f.seek(0)
		f.write(new_update)
		f.truncate()
	else:
		now = datetime.now()
		print(now.strftime("%H:%M:%S"), "no updates")
	f.close()
	
	return [cs_results, ps_results, warn_results]

#force indicates whether it was a forced update by a user, or a daily check
#idx indicates the rank at which we're going to start printing to Discord
#sortParam is applicable only when type="Medal" or type="Trophy", and represents what we sort by
#for medals, sortParam 0 = plat, 1 = gold, 2 = silver, 3 = bronze
#for trophies, sortParam 0 = points, 1 = plats, and 2-6 represent gold, silver, bronze, 4th, 5th
def scrape_leaderboard(type, force, idx, sortParam = 0):
	#open previous leaderboard data
	if type == "Starboard":
		URL = "https://cyberscore.me.uk/scoreboards/starboard"
		f = open("leaderboards/starboard.csv", "r+")
	elif type == "Medal":
		URL = "https://cyberscore.me.uk/scoreboards/medal"
		f = open("leaderboards/medals.csv", "r+")
		if sortParam == 1:
			URL += "?manual_sort=gold"
		elif sortParam == 2:
			URL += "?manual_sort=silver"
		elif sortParam == 3:
			URL += "?manual_sort=bronze"
	elif type == "Trophy":
		URL = "https://cyberscore.me.uk/scoreboards/trophy"
		f = open("leaderboards/trophy.csv", "r+")
		if sortParam == 1:
			URL += "?manual_sort=platinum"
		elif sortParam == 2:
			URL += "?manual_sort=gold"
		elif sortParam == 3:
			URL += "?manual_sort=silver"
		elif sortParam == 4:
			URL += "?manual_sort=bronze"
		elif sortParam == 5:
			URL += "?manual_sort=4th"
		elif sortParam == 6:
			URL += "?manual_sort=5th"
	elif type == "Arcade":
		URL = "https://cyberscore.me.uk/scoreboards/arcade"
		f = open("leaderboards/arcade.csv", "r+")
	elif type == "Solution":
		URL = "https://cyberscore.me.uk/scoreboards/solution"
		f = open("leaderboards/solution.csv", "r+")
	elif type == "Challenge":
		URL = "https://cyberscore.me.uk/scoreboards/challenge"
		f = open("leaderboards/challenge.csv", "r+")
	elif type == "Collectible":
		URL = "https://cyberscore.me.uk/scoreboards/collectible"
		f = open("leaderboards/collectible.csv", "r+")
	elif type == "Incremental":
		URL = "https://cyberscore.me.uk/scoreboards/incremental"
		f = open("leaderboards/incremental.csv", "r+")
	elif type == "Level":
		URL = "https://cyberscore.me.uk/scoreboards/incremental?manual_sort=cxp"
		f = open("leaderboards/level.csv", "r+")
	elif type == "Rainbow":
		URL = "https://cyberscore.me.uk/scoreboards/rainbow"
		f = open("leaderboards/rainbow.csv", "r+")
	elif type == "Proof":
		URL = "https://cyberscore.me.uk/scoreboards/proof"
		f = open("leaderboards/proof.csv", "r+")
	elif type == "Video":
		URL = "https://cyberscore.me.uk/scoreboards/vproof"
		f = open("leaderboards/vproof.csv", "r+")
	elif type == "Submissions":
		URL = "https://cyberscore.me.uk/scoreboards/submissions"
		f = open("leaderboards/submissions.csv", "r+")
	elif type == "Speedrun":
		URL = "https://cyberscore.me.uk/scoreboards/speedrun"
		f = open("leaderboards/speedrun.csv", "r+")

	previous_update = load_leaderboard(f)

	#perform web scrape
	page = requests.get(URL)
	soup = BeautifulSoup(page.content, "html.parser")
	table = soup.find(id="scoreboard_classic")
	players = list(table.find_all("tr"))
	
	#Some boards have a header, so strip that
	if (type == "Rainbow" or type == "Submissions" or type == "Incremental" 
	or type == "Proof" or type == "Video" or type == "Speedrun" or type == "Level"
	or type == "Medal" or type == "Trophy"):
		players.pop(0)

	#work out how many players we have to scrape
	#with current site UI this should be a maximum of 100, but fewer if the leaderboard
	#doesn't have 100 unique entrants
	player_count = len(players)

	output = ""
	save_data = ""
	for i in range(0, player_count): #iterate over each player
		player = players[i]

		user_cell = player.find(class_="name").a
		user = user_cell.get_text()
		#users are listed as e.g., 'John “N00bSl4y3r69” Doe', so extract only the alias
		#note the use of "smart quotes" (“”) and not regular ones ("")
		matches = re.findall(r'“([^”]*)”', user)
		if(matches):
			user_name = matches[0]
		else: #if there's no matches use the full string
			user_name = user
		user_link = user_cell["href"]
		
		#strip the text denoting the score type
		#note that "scoreboardCSR" is actually the correct classname for arcade/solution
		if type == "Starboard":
			score_raw = player.find(class_="scoreboardCSR").get_text().strip()
			score = float(score_raw.removesuffix(" CSR").replace(",",""))
		elif type == "Medal":
			medals = player.find_all(class_="medals")
			score_raw = medals[sortParam].get_text().strip()
			score = int(score_raw.replace(",",""))
		elif type == "Trophy":
			trophies = player.find_all(class_="medals")
			score_raw = trophies[sortParam].get_text().strip()
			score = int(score_raw.replace(",",""))
		elif type == "Arcade":
			score_raw = player.find(class_="scoreboardCSR").get_text().strip()
			score = int(score_raw.removesuffix(" Tokens").replace(",",""))
		elif type == "Solution":
			score_raw = player.find(class_="scoreboardCSR").get_text().strip()
			score = int(score_raw.removesuffix(" Brain Power").replace(",",""))
		elif type == "Challenge":
			score_raw = player.find(class_="scoreboardCSR").get_text().strip()
			score = float(score_raw.removesuffix(" Style Points").replace(",",""))
		elif type == "Collectible":
			score_raw = player.find(class_="scoreboardCSR").get_text().strip()
			score = int(score_raw.removesuffix(" Cyberstars").replace(",",""))
		elif type == "Incremental":
			#incremental is a bit odd as there's two important metrics
			inc_scores = list(player.find_all(class_="scoreboardCSR"))
			#for the incremental score we display "VXP" instead of "Versus XP"
			#this is done solely due to embed size constraints
			score_raw = inc_scores[0].get_text().strip().replace("Versus ","V")
			score = int(score_raw.removesuffix(" VXP").replace(",",""))
			inc_level_raw = inc_scores[1].contents[1].strip()
			#level will never reach 1,000 so no comma replacement needed
			#we also don't do any maths with it so don't need to store as int
			inc_level = inc_level_raw.removeprefix("Level ")
		elif type == "Level":
			#for level we want to actually get the raw CXP and reverse-engineer the level from that
			#this allows us to display sub-integer changes
			cxp_raw = list(player.find_all(class_="scoreboardCSR"))[1].contents[2].get_text()
			cxp = int(cxp_raw.strip().replace(",","").replace("(","").replace(")","").removesuffix(" CXP"))
			score = math.log(max(10, cxp)/10, 2.5) + 1 #a user with 0xp starts at level 1
			score = round(score, 2) #round it to 2dp for display purposes
			integer_level = math.floor(score)
			decimal_level = round((score - integer_level) * 100)
			score_raw = "Level " + str(integer_level) + " [" + str(decimal_level) + "%]"
		elif type == "Rainbow":
			score_raw = player.h2.get_text()
			score = int(score_raw.removesuffix(" RP").replace(",",""))
		elif type == "Submissions" or type == "Proof" or type == "Video":
			score_raw = player.b.get_text()
			score = int(score_raw.replace(",",""))
		elif type == "Speedrun":
			score_raw = player.find(class_="medals").get_text().strip()
			score = cmfn.time_to_seconds(score_raw)

		#in some cases score_raw includes excess whitespace
		#e.g., "382,193     Brain Power"
		#so we strip that. This occurs only on the Solution board, but
		#no harm in running it on all boards just in case that changes
		score_raw = ' '.join(score_raw.split())

		#check position changes using the read file data
		#we don't store positions for medal table non-default sorts, so exclude that
		if user_name in previous_update and not sortParam:
			user_data = previous_update[user_name]
			pos_change = user_data['pos'] - (i+1)
			score_change = score - user_data['score']
			
			#for alignment we're using U+2800 braille spaces - "⠀" for non-pos changes
			#and U+200A hair spaces - " " for pos changes
			#this aligns better than anything else Discord will indent with

			if pos_change == 0:
				pos_change_str = "⠀"*3
			elif pos_change > 0:
				pos_change_str = "▲"+str(pos_change)+(" "*8)
			else:
				pos_change_str = "▼"+str(abs(pos_change))+(" "*8)
		else:
			if sortParam:
				pos_change_str = ""
			else:
				pos_change_str = ":new:"+(" "*8)
			score_change = 0

		#Starboard+Challenge+Level requires decimal formatting for output, Speedrun requires time
		#other boards are integers
		if type == "Starboard":
			score_str = "{:,.2f}".format(score)
			if score_change:
				score_change_str = " ({:+,.2f})".format(score_change)
		elif type == "Challenge":
			score_str = "{:,.1f}".format(score)
			if score_change:
				score_change_str = " ({:+,.1f})".format(score_change)
		elif type == "Speedrun":
			score_str = cmfn.seconds_to_time(score)
			if score_change:
				symbol = ""
				if score_change > 0:
					symbol = "+"
				elif score_change < 0:
					symbol = "-"
				score_change_str = " ("+symbol+cmfn.seconds_to_time(score_change)+")"
		elif type == "Level":
			score_str = "{:,.2f}".format(score)
			if score_change:
				symbol = ""
				if score_change > 0:
					symbol = "+"
				elif score_change < 0:
					symbol = "-"
				score_change_str = " ("+symbol+str(round(score_change*100))+"%)"
		else:
			#score is stored as a float to support CSR
			#but other boards have integer scores, so we convert to that for representation
			score_change = int(score_change)
			score_str = "{:,}".format(score)
			if score_change:
				score_change_str = " ({:+,})".format(score_change)

		#if we didn't have a score change, set an empty differential string
		if not score_change:
			score_change_str = ""
		
		#the idx paramater indicates the start of the range that's displayed in Discord
		#since we need to include 10 players, the start can be no more than player_count-10
		#so we clamp the index between 0 and that
		idx = max(0, min(player_count-10, idx))
		
		#a total of 10 users are displayed, starting at idx
		if i in range(idx, idx+10):
			#todo - if the user is in the top three, use a medal instead of position
			output += pos_change_str + str(i+1) + ". "
			output += "["+user_name+"]("+CS_PREFIX+user_link+") - "
			output += score_raw+score_change_str
			#if we're running the incremental scoreboard include level
			if type == "Incremental":
				output += " [L" + inc_level + "]"
			output += "\n"
		
		#and add it to the leaderboard .csv
		if type == "Speedrun":
			save_data += str(i+1) + "," + user_name + "," + str(score) + "\n"
		else:
			save_data += str(i+1) + "," + user_name + "," + score_str.replace(",","") + "\n"

	#only save the data if we did a daily update, so that score diffs are always relative
	#to midnight UTC that day, and can't be disrupted by debugging
	#we also avoid saving if we did a medal table scrape with a non-default sort
	if(not force and not sortParam): #adjust this to force-overwrite
		save_leaderboard(save_data, f)
	f.close()

	return output

def scrape_top_submitters(days, idx, type): #type = "user" or "game"
	URL = "https://cyberscore.me.uk/latest_subs_stats.php?updates=no&days=" + str(days)

	#perform web scrape
	page = requests.get(URL)
	soup = BeautifulSoup(page.content, "html.parser")

	if type == "user":
		entries = list(soup.find(id="pageright").find("table").find_all("tr"))
	elif type == "game":
		entries = list(soup.find(id="pageleft").find("table").find_all("tr"))
		#games have a header row while players don't, so pop that
		entries.pop(0)

	#we want to get the first 10 entries starting at idx
	#if fewer than 10 entries exist, we also take some before idx if possible
	#e.g., if we start at 20th and only 25 entries exist, we'll actually end up printing 16th-25th
	#also note that idx is already zero-indexed as that conversion happened on processing the parameters
	output = ""
	if len(entries) > 10 and idx > 0:
		idx = min(idx, len(entries)-10)

	i = max(0, idx)
	while i < min(10+idx, len(entries)):
		entry = entries[i]
		cells = list(entry.find_all("td"))

		entry_name = cells[0].get_text().strip()
		entry_link = cells[0].a['href']
		#users have score in cell 1, games have *records* there so we need to go to cell 2
		if type == "user":
			entry_score = cells[1].get_text().strip()
		elif type == "game":
			entry_score = cells[2].get_text().strip()
			#also for some reason users have an explicit domain but games don't, so add that if needed
			entry_link = "https://cyberscore.me.uk" + entry_link

		output += "["+entry_name+"]("+entry_link+")" + " - " + entry_score + " submissions\n"
		i+=1

	#generate the range string for what section of the list we generated
	range_min = idx+1 #we want to output the first entry as #1, not #0
	range_max = min(idx+10, len(entries))
	range_string = "#"+str(range_min)+"–#"+str(range_max)+" of "+str(len(entries))

	#and output results
	return [output, range_string]

def scrape_profile(username):
	URL = "https://cyberscore.me.uk/profile-api/"+username+".json"
	page = requests.get(URL)
	user = json.loads(page.content)
	#hardcode values just so we can start to build an embed
	print(URL)
	
	#API has a pending merge request to change scoreboard_pos to rainbow_pos
	#so we check if scoreboard_pos exists, and if not, use rainbow_pos
	if "scoreboard_pos" in user['positions']:
		rainbow_pos = user['positions']['scoreboard_pos']
	else:
		rainbow_pos = user['positions']['rainbow_pos']
	
	user_data = {
		"username": user['username'],
		"user_id": user['user_id'],
		"records": {
			"total":user['sub_counts']['total'],
			"medal":user['sub_counts']['ranked'],
			"speedrun":user['sub_counts']['speedrun'],
			"solution":user['sub_counts']['solution'],
			"unranked":user['sub_counts']['unranked'],
			"collectible":0, #not supported by API yet
			"incremental":0, #not supported by API yet
			"challenge":user['sub_counts']['challenge'],
			"arcade":user['sub_counts']['arcade']
		},
		"proofs": {
			"total":user['proof_counts']['total'],
			"medal":user['proof_counts']['ranked'],
			"speedrun":user['proof_counts']['speedrun'],
			"solution":user['proof_counts']['solution'],
			"unranked":user['proof_counts']['unranked'],
			"collectible":0, #not supported by API yet
			"incremental":0, #not supported by API yet
			"challenge":user['proof_counts']['challenge'],
			"arcade":user['proof_counts']['arcade'],
		},
		"video proofs": {
			"total":user['video_proof_counts']['total'],
			"medal":user['video_proof_counts']['ranked'],
			"speedrun":user['video_proof_counts']['speedrun'],
			"solution":user['video_proof_counts']['solution'],
			"unranked":user['video_proof_counts']['unranked'],
			"collectible":0, #not supported by API yet
			"incremental":0, #not supported by API yet
			"challenge":user['video_proof_counts']['challenge'],
			"arcade":user['video_proof_counts']['arcade'],
		},
		"positions": {
			"starboard":user['positions']['starboard_pos'],
			"medal":user['positions']['medal_pos'],
			"trophy":user['positions']['trophy_pos'],
			"rainbow":rainbow_pos,
			"arcade":user['positions']['arcade_pos'],
			"speedrun":user['positions']['speedrun_pos'],
			"solution":user['positions']['solution_pos'],
			"challenge":user['positions']['challenge_pos'],
			"collectible":user['positions']['collectible_pos'],
			"incremental":user['positions']['incremental_pos'],
			"submissions":user['positions']['total_submissions_pos'],
			"proof":user['positions']['proof_pos'],
			"video":user['positions']['video_proof_pos'],
			"average":str(round(user['avg_rainbow_rank'],2)),
		}
	}

	return user_data
	

#file is an actual file hook, *not* a path
def load_leaderboard(file):
	data = {}

	line = file.readline()
	while line:
		player = line.split(",")
		pos = int(player[0])
		name = player[1]
		if ":" in player[2]: #special handling for speedruns since it's bugged
			score = cmfn.time_to_seconds(player[2])
		else:
			score = float(player[2]) #only a float for some boards
		data[name] = {"pos": pos, "score": score}
		line = file.readline()
	
	return data

#file is an actual file hook, *not* a path
def save_leaderboard(save_data, file):
	file.seek(0)
	file.write(save_data)
	file.truncate()
	return