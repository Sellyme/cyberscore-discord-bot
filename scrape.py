import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import math

CS_PREFIX = "https://cyberscore.me.uk"

def scrape_latest():
	URL = "https://cyberscore.me.uk/latest-submissions"
	cs_results = [] #messages to output to Cyberscore Discord
	ps_results = [] #messages to output to New Pokemon Snap Discord

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
		flag_emoji = get_flag_emoji(country)
		
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
		

	#once we've iterated over everything we can save the last update date
	if new_update > last_update:
		f.seek(0)
		f.write(new_update)
		f.truncate()
	else:
		now = datetime.now()
		print(now.strftime("%H:%M:%S"), "no updates")
	f.close()
	
	return [cs_results, ps_results]

#force indicates whether it was a forced update by a user, or a daily check
def scrape_leaderboard(type, force, idx):
	
	#open previous leaderboard data
	if type == "Starboard":
		URL = "https://cyberscore.me.uk/scoreboards/starboard"
		f = open("leaderboards/starboard.csv", "r+")
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
	or type == "Proof" or type == "Video" or type == "Speedrun" or type == "Level"):
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
			score = float(score_raw.rstrip(" CSR").replace(",",""))
		elif type == "Arcade":
			score_raw = player.find(class_="scoreboardCSR").get_text().strip()
			score = int(score_raw.rstrip(" Tokens").replace(",",""))
		elif type == "Solution":
			score_raw = player.find(class_="scoreboardCSR").get_text().strip()
			score = int(score_raw.rstrip(" Brain Power").replace(",",""))
		elif type == "Challenge":
			score_raw = player.find(class_="scoreboardCSR").get_text().strip()
			score = float(score_raw.rstrip(" Style Points").replace(",",""))
		elif type == "Collectible":
			score_raw = player.find(class_="scoreboardCSR").get_text().strip()
			score = int(score_raw.rstrip(" Cyberstars").replace(",",""))
		elif type == "Incremental":
			#incremental is a bit odd as there's two important metrics
			inc_scores = list(player.find_all(class_="scoreboardCSR"))
			#for the incremental score we display "VXP" instead of "Versus XP"
			#this is done solely due to embed size constraints
			score_raw = inc_scores[0].get_text().strip().replace("Versus ","V")
			score = int(score_raw.rstrip(" VXP").replace(",",""))
			inc_level_raw = inc_scores[1].contents[0].strip()
			#level will never reach 1,000 so no comma replacement needed
			#we also don't do any maths with it so don't need to store as int
			inc_level = inc_level_raw.lstrip("Level ")
		elif type == "Level":
			#for level we want to actually get the raw CXP and reverse-engineer the level from that
			#this allows us to display sub-integer changes
			cxp_raw = list(player.find_all(class_="scoreboardCSR"))[1].contents[3].get_text()
			cxp = int(cxp_raw.strip().rstrip(" CXP").replace(",",""))
			score = math.log(max(10, cxp)/10, 2.5) + 1 #a user with 0xp starts at level 1
			score = round(score, 2) #round it to 2dp for display purposes
			score_raw = "Level " + "{:.2f}".format(score)
		elif type == "Rainbow":
			score_raw = player.h2.get_text()
			score = int(score_raw.rstrip(" RP").replace(",",""))
		elif type == "Submissions" or type == "Proof" or type == "Video":
			score_raw = player.b.get_text()
			score = int(score_raw.replace(",",""))
		elif type == "Speedrun":
			score_raw = player.find(class_="medals").get_text().strip()
			score = time_to_seconds(score_raw)

		#in some cases score_raw includes excess whitespace
		#e.g., "382,193     Brain Power"
		#so we strip that. This occurs only on the Solution board, but
		#no harm in running it on all boards just in case that changes
		score_raw = ' '.join(score_raw.split())

		#check position changes using the read file data
		if user_name in previous_update:
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
			pos_change_str = ":new:"+(" "*8)
			score_change = 0

		#Starboard+Challenge+Level requires decimal formatting for output, Speedrun requires time
		#other boards are integers
		if type == "Starboard" or type == "Level":
			score_str = "{:,.2f}".format(score)
			if score_change:
				score_change_str = " ({:+,.2f})".format(score_change)
		elif type == "Challenge":
			score_str = "{:,.1f}".format(score)
			if score_change:
				score_change_str = " ({:+,.1f})".format(score_change)
		elif type == "Speedrun":
			score_str = seconds_to_time(score)
			if score_change:
				symbol = ""
				if score_change > 0:
					symbol = "+"
				elif score_change < 0:
					symbol = "-"
				score_change_str = " ("+symbol+seconds_to_time(score_change)+")"
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
	if(not force): #adjust this to force-overwrite
		save_leaderboard(save_data, f)
	f.close()

	return output

def scrape_top_submitters(days):
	URL = "https://cyberscore.me.uk/latest_subs_stats.php?updates=no&days=" + str(days)

	#perform web scrape
	page = requests.get(URL)
	soup = BeautifulSoup(page.content, "html.parser")
	players = list(soup.find(id="pageright").find("table").find_all("tr"))
	
	#iterate over the top 10
	i = 0
	output = ""
	while i < min(10, len(players)):
		player = players[i]
		cells = list(player.find_all("td"))
		
		user_name = cells[0].get_text().strip()
		user_link = cells[0].a['href']
		user_score = cells[1].get_text().strip()

		output += "["+user_name+"]("+user_link+")" + " - " + user_score + " submissions\n"
		i+=1
	return output

def time_to_seconds(time_str):
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)

def seconds_to_time(seconds):
	#the maths here fails dismally with negative numbers
	#since we need to support negatives (for score differentials)
	#we just take the absolute value of the input
	seconds = abs(seconds)
	h = str(math.floor(seconds/3600)).zfill(2)
	seconds = seconds % 3600
	m = str(math.floor(seconds/60)).zfill(2)
	seconds = int(seconds % 60)
	s = str(seconds).zfill(2)
	return h+":"+m+":"+s


def get_flag_emoji(country_code):
	#Cyberscore flag codes don't exactly match Discord emoji codes
	#Mainly with "Unknown", and dependencies/constituent countries
	#So we hard code handling for those
	if country_code == "--":
		flag_emoji = ":pirate_flag:"
	elif country_code == "x1":
		flag_emoji = ":england:"
	elif country_code == "x2":
		flag_emoji = ":scotland:"
	elif country_code == "x3":
		flag_emoji = ":wales:"
	else:
		flag_emoji = ":flag_" + country_code + ":"
	return flag_emoji

#file is an actual file hook, *not* a path
def load_leaderboard(file):
	data = {}

	line = file.readline()
	while line:
		player = line.split(",")
		pos = int(player[0])
		name = player[1]
		if ":" in player[2]: #special handling for speedruns since it's bugged
			score = time_to_seconds(player[2])
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