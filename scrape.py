import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

CS_PREFIX = "https://cyberscore.me.uk"
last_update_time = 0 #todo - set this to startup or a saved time

def scrape_latest():
	URL = "https://cyberscore.me.uk/latest_subs.php"
	results = []

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
	
	#iterate over all records
	for record in records:
		columns = list(record.find_all("td"))
		#skip any records we've already scanned
		date = columns[10].get_text()
		if date <= last_update:
			#print ("Skipping update on", date, "as it is before", last_update)
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
		uc_col = columns[9] #check exact function here

		country = flag_col.img.get('alt').lower()
		flag_emoji = get_flag_emoji(country)
		
		user_name = name_col.a.get_text()
		user_link = name_col.a['href']
		user = "["+user_name+"]("+CS_PREFIX+user_link+")"
		
		game_name = game_col.strong.get_text()
		game_link = game_col.a['href']
		game = "["+game_name+"]("+CS_PREFIX+game_link+")"
		
		chart_links = list(chart_col.find_all('a'))
		#group names don't exist for all charts, so we need to check chart_links length
		#and only construct group name if > 1
		if(len(chart_links) > 1):
			group_name = chart_links[0].get_text()
			chart_name = chart_links[1].get_text()
			chart_link = chart_col.find_all('a')[1]['href']
			chart = "["+group_name + " → " + chart_name+"]("+CS_PREFIX+chart_link+")"
		else:
			chart_name = chart_links[0].get_text()
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
		
		pos = pos_col.get_text().replace(" ","")
		csr = award_col.strong
		#csr is not displayed for UC charts, so display Challenge Points instead
		if csr:
			csr = csr.get_text().strip()
		else:
			csr = award_col.span.get_text()

		#construct string
		output = flag_emoji + " " + user + " just scored " + score
		output += " (Pos: **" + pos + "**" + medal + " · " + csr+")\n"
		output += game + " → " + chart
		output += comment #if the comment exists it will appear italicised on a new line
		
		results.append(output)

	#once we've iterated over everything we can save the last update date
	if new_update > last_update:
		f.seek(0)
		f.write(new_update)
		f.truncate()
	else:
		now = datetime.now()
		print(now.strftime("%H:%M:%S"), "no updates")
	f.close()
	
	return results

#force indicates whether it was a forced update by a user, or a daily check
def scrape_leaderboard(type, force, idx):
	
	#open previous leaderboard data
	if type == "Mainboard":
		URL = "https://cyberscore.me.uk/scoreboard.php"
		f = open("leaderboards/mainboard.csv", "r+")
	elif type == "Arcade":
		URL = "https://cyberscore.me.uk/scoreboard.php?board=8"
		f = open("leaderboards/arcade.csv", "r+")
	elif type == "Solution":
		URL = "https://cyberscore.me.uk/scoreboard.php?board=13"
		f = open("leaderboards/solution.csv", "r+")
	elif type == "Rainbow":
		URL = "https://cyberscore.me.uk/scoreboard.php?board=12"
		f = open("leaderboards/rainbow.csv", "r+")

	previous_update = load_leaderboard(f)

	#perform web scrape
	page = requests.get(URL)
	soup = BeautifulSoup(page.content, "html.parser")
	table = soup.find(id="scoreboard_classic")
	players = list(table.find_all("tr"))
	
	#rainbow board has a header, other boards don't, so strip that
	if type == "Rainbow":
		players.pop(0)
	#todo - finish rainbow handling

	output = ""
	save_data = ""
	for i in range(0,100): #iterate over the top 100 players
		player = players[i]
		
		country_code = player.find(class_="flag").img["alt"].lower()
		flag_emoji = get_flag_emoji(country_code)
		
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
		
		#note that despite the class name "scoreboardCSR"
		#this is actually still correct for arcade/solution
		score_raw = player.find(class_="scoreboardCSR").get_text().strip()
		#strip the text denoting the score type
		if type == "Mainboard":
			score = float(score_raw.rstrip(" CSR").replace(",",""))
		elif type == "Arcade":
			score = int(score_raw.rstrip(" Tokens").replace(",",""))
		elif type == "Solution":
			score = int(score_raw.rstrip(" Brain Power").replace(",",""))
		
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

		#mainboard requires decimal formatting for output, other boards are integers
		if type == "Mainboard":
			score_str = "{:,.2f}".format(score)
			if score_change:
				score_change_str = " ({:+,.2f})".format(score_change)
			else:
				score_change_str = ""
		else:
			#score is stored as a float to support CSR
			#but other boards have integer scores, so we convert to that for representation
			score_change = int(score_change)
			score_str = "{:,}".format(score)

			if score_change:
				score_change_str = " ({:+,})".format(score_change)
			else:
				score_change_str = ""
		
		#the idx paramater indicates the start of the range that's displayed in Discord
		#we only have the top 100, so idx can be at most 90
		idx = max(0, min(90, idx)) #clamps idx to 0-90 inclusive
		
		#a total of 10 users are displayed, starting at idx
		if i in range(idx, idx+10):
			#todo - if the user is in the top three, use a medal instead of position
			output += pos_change_str + str(i+1) + ". "
			output += "["+user_name+"]("+CS_PREFIX+user_link+") - "
			output += score_raw+score_change_str+"\n"
		
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

		output += "["+user_name+"]("+CS_PREFIX+user_link+")" + " - " + user_score + " submissions\n"
		i+=1
	return output
	

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