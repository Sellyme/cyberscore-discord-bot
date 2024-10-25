import math, os, re
from datetime import datetime

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

def get_file_by_year(year, file_dir):
	#takes an input year, and finds the *most recent* file in a directory matching that year
	#this assumes all files in the directory have their yyyy-mm-dd timestamp as a filename prefix
	year = str(year)
	files = []

	for filename in os.listdir(file_dir):
		if filename.startswith(year):
			files.append(filename)

	#if there's no files, error out
	if len(files) == 0:
		print("ERROR: no files found in dir '" + file_dir + "' matching requested year '" + year + "'")
		return False

	#sort all the files and take the last alphabetically (which will be the closest to the end of year)
	req_file = sorted(files, reverse=True)[0]
	#print("DEBUG: pulling file ", req_file)
	return req_file

def get_scoreboard_names(board_type, sortParam = 0):
	#takes in a consistent human-readable name of a specific scoreboard, and an optional sort poram
	#returns an array containing the name used as the site's URL for that board,
	#the name used for the filesystem where archives are stored, and the sort parameter name

	#set defaults
	site_name = board_type.lower()
	file_name = board_type.lower()
	sortType = ""

	#handle custom sortParams, and override for any name mismatches
	if board_type == "Medal":
		site_name = "medal"
		file_name = "medals"
		if sortParam == 1:
			sortType = "gold"
		elif sortParam == 2:
			sortType = "silver"
		elif sortParam == 3:
			sortType = "bronze"
	elif board_type == "Trophy":
		if sortParam == 1:
			sortType = "platinum"
		elif sortParam == 2:
			sortType = "gold"
		elif sortParam == 3:
			sortType = "silver"
		elif sortParam == 4:
			sortType = "bronze"
		elif sortParam == 5:
			sortType = "4th"
		elif sortParam == 6:
			sortType = "5th"
	elif board_type == "Level":
		site_name = "incremental"
		sortType = "cxp"
	elif board_type == "Video":
		site_name = "vproof"
		file_name = "vproof"

	#and return the results
	return [site_name, file_name, sortType]

def get_leaderboard_from_disk(file_name, ytd = False):
	#parses and returns a leaderboard of the specified size_type from a certain date.
	#date can be specified by optional parameters (many potential ones unimplemented)
	#but is by default the most recent *daily* leaderboard update available

	#if the ytd flag is set, load the *final* update from the previous calendar year
	if ytd:
		#get current year and subtract one
		req_year = int(datetime.now().strftime('%Y')) - 1
		#build a list of all files from the requested year
		location = "leaderboards/archive/"+file_name+"/"
		req_file = get_file_by_year(req_year, location)
		if not req_file:
			return False
		last_year = open(location+req_file, "r+")
		result = load_leaderboard(last_year)
	else: #otherwise, load the most recently saved file
		latest = open("leaderboards/"+file_name+".csv", "r+")
		result = load_leaderboard(latest)

	return result

#file is an actual file hook, *not* a path
def load_leaderboard(file, idx_by_pos = False):
	#if idx_by_pos is set, each element in the dictionary is indexed by the leaderboard position
	#otherwise, they're indexed by username
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
		if idx_by_pos:
			data[pos] = {"name": name, "score": score}
		else:
			data[name] = {"pos": pos, "score": score}
		line = file.readline()

	return data

def scrape_leaderboard_new(): #rename when done
	#todo - reimplement all of the leaderboard scraping here
	#and instead of building a string, build a rich datastructure
	#that we can then use to output differently-sorted results
	#(e.g., order a CSR leaderboard by gains instead of total)
	return False

def convert_timestamp_to_excel(timestamp):
	#replaces the YYYY-MM-DD_HH-MM-SS.csv format leaderboard files are saved using
	#with the YYYY-MM-DD HH:MM:SS format used for date processing in Excel
	return re.sub(r"(\d\d\d\d-\d\d-\d\d)_(\d\d)-(\d\d)-(\d\d).*", "\g<1> \g<2>:\g<3>:\g<4>", timestamp)

def clean_username(user):
	#users are listed as e.g., 'John “N00bSl4y3r69” Doe', so extract only the alias
	#note the use of "smart quotes" (“”) and not regular ones ("")
	matches = re.findall(r'“([^”]*)”', user)
	if matches:
		user_name = matches[0]
	else: #if there's no matches use the full string
		user_name = user

	return user_name

def get_award_name(board_type):
	#TODO - fold this into get_scoreboard_names() and genericise the latter's capitalisation
	board_type = board_type.lower()
	if board_type == "starboard":
		return "CSR"
	elif board_type == "medal" or board_type == "medals":
		return "Medals"
	elif board_type == "trophy" or board_type == "trophies":
		return "Trophy Points"
	elif board_type == "arcade":
		return "Tokens"
	elif board_type == "solution":
		return "Brain Power"
	elif board_type == "challenge":
		return "Style Points"
	elif board_type == "collectible":
		return "Cyberstars"
	elif board_type == "incremental":
		return "VXP" #incremental board is VXP by default, we separate CXP into a Level board
	elif board_type == "level":
		return "CXP"
	elif board_type == "rainbow":
		return "Rainbow Power"
	elif board_type == "submissions" or board_type == "subs":
		return "Submissions"
	elif board_type == "proof":
		return "Proofs"
	elif board_type == "video" or board_type == "vproof":
		return "Video proofs"
	elif board_type == "speedrun":
		return "Speed" #official name is "Speedrun Time" but that's a bit weird and ambiguous