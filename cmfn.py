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
	return req_file

def get_file_by_sort(sort_type, file_dir):
	#takes an input sort parameter, and finds the most recent file in a directory matching that sort
	#this assumes all files in the directory have their yyyy-mm-dd timestamp as a filename prefix
	#and additionally that files have a `_suffix` in their name indicating their sort parameter
	#this function never gets called for default sortParams, so we can ignore any file without that suffix

	files = []
	for filename in os.listdir(file_dir):
		if sort_type in filename:
			files.append(filename)

	#if there's no files, error out
	if len(files) == 0:
		print("ERROR: no files found in dir '" + file_dir + "' matching requested sort '" + sort_type + "'")
		return False

	#sort all the files and take the last alphabetically (which will be the most recent)
	req_file = sorted(files, reverse=True)[0]
	return req_file

def get_sort_param(board_type, args):
	#takes in a board type + list of arguments from a user command and looks for sort flags
	#e.g., an argument that says "-g" suggests sorting by gold medals/trophies
	sortParam = None
	board_type = board_type.lower()

	#convert all args to lowercase for checking
	args = [x.lower() for x in args]

	if board_type.startswith("medal"):
		if "-g" in args or "gold" in args:
			sortParam = 1
		elif "-s" in args or "silver" in args:
			sortParam = 2
		elif "-b" in args or "bronze" in args:
			sortParam = 3
		else:
			sortParam = 0
	elif board_type.startswith("troph"):
		if "-p" in args or "platinum" in args or "plat" in args:
			sortParam = 1
		elif "-g" in args or "gold" in args:
			sortParam = 2
		elif "-s" in args or "silver" in args:
			sortParam = 3
		elif "-b" in args or "bronze" in args:
			sortParam = 4
		elif "-4" in args or "4th" in args:
			sortParam = 5
		elif "-5" in args or "5th" in args:
			sortParam = 6
		else:
			sortParam = 0
	#we don't have sortparams for level vs cxp, because those are treated as separate boards
	return sortParam

def get_scoreboard_names(board_type, sortParam = 0):
	#takes in a consistent human-readable name of a specific scoreboard, and an optional sort poram
	#returns an array containing the name used as the site's URL for that board,
	#the name used for the filesystem where archives are stored, and the sort parameter name

	#set defaults
	display_name = None
	board_type = board_type.lower() #normalise this to avoid case-sensitive matching
	site_name = None
	file_name = None
	award_name = None
	sort_type = ""

	match board_type:
		case "medal" | "medal table" | "medals":
			site_name = "medal"
			file_name = "medals"
			display_name = "Medals"
			if sortParam == 1:
				sort_type = "gold"
			elif sortParam == 2:
				sort_type = "silver"
			elif sortParam == 3:
				sort_type = "bronze"
			else:
				sort_type = "platinum"
			award_name = (sort_type + " " + file_name).title() #e.g., "Gold Medals"
		case "trophy" | "trophy table" | "trophies":
			site_name = "trophy"
			file_name = "trophy"
			#for display_name we use "trophy table" because just "trophies" would be misleading
			#as the default sort is trophy points, not trophy count.
			#this is not the case for the medal table, where "Medals" is indeed the default sort and a good title
			display_name = "Trophy Table"
			if sortParam == 1:
				sort_type = "platinum"
				award_name = "Platinum Trophies"
			elif sortParam == 2:
				sort_type = "gold"
				award_name = "Gold Trophies"
			elif sortParam == 3:
				sort_type = "silver"
				award_name = "Silver Trophies"
			elif sortParam == 4:
				sort_type = "bronze"
				award_name = "Bronze Trophies"
			elif sortParam == 5:
				sort_type = "4th"
				award_name = "4th Place Trophies"
			elif sortParam == 6:
				sort_type = "5th"
				award_name = "5th Place Trophies"
			else:
				sort_type = None
				award_name = "Trophy Points"
		case "level" | "cxp":
			site_name = "incremental"
			file_name = "level"
			display_name = "Level"
			sort_type = "cxp"
			award_name = "Level" #your score is displayed in units of Level, not of CXP
		case "video" | "vproof" | "video proof" | "videos" | "video proofs":
			site_name = "vproof"
			file_name = "vproof"
			display_name = "Video Proof"
			award_name = "Videos"
		case "proof" | "proofs":
			site_name = "proof"
			file_name = "proof"
			display_name = "Proof"
			award_name = "Proofs"
		case "arcade" | "tokens":
			site_name = "arcade"
			file_name = "arcade"
			display_name = "Arcade"
			award_name = "Tokens"
		case "challenge" | "uc" | "user challenge" | "sp" | "style points":
			site_name = "challenge"
			file_name = "challenge"
			display_name = "User Challenge"
			award_name = "Style Points"
		case "collectible" | "collectible" | "cyberstars" | "stars":
			site_name = "collectible"
			file_name = "collectible"
			display_name = "Collector's Cache"
			award_name = "Cyberstars"
		case "incremental" | "vxp":
			site_name = "incremental"
			file_name = "incremental"
			display_name = "Experience"
			award_name = "VXP"
		case "rainbow" | "rp":
			site_name = "rainbow"
			file_name = "rainbow"
			display_name = "Rainbow"
			award_name = "Rainbow Power"
		case "solution" | "brain power" | "bp":
			site_name = "solution"
			file_name = "solution"
			display_name = "Solution"
			award_name = "Brain Power"
		case "speedrun":
			site_name = "speedrun"
			file_name = "speedrun"
			display_name = "Speedrun"
			award_name = "Speedrun Time"
		case "starboard" | "mainboard" | "csr":
			site_name = "starboard"
			file_name = "starboard"
			display_name = "Starboard"
			award_name = "CSR"
		case "submissions" | "subs":
			site_name = "submissions"
			file_name = "submissions"
			display_name = "Submissions"
			award_name = "Submissions"

	#and return the results
	return {
		'site_name': site_name,
		'file_name': file_name,
		'display_name': display_name,
		'award_name': award_name,
		'sort_type': sort_type,
	}

def get_leaderboard_from_disk(file_name, ytd = False, sort_type = ""):
	#parses and returns a leaderboard of the specified type from a certain date.
	#date can be specified by optional parameters (many potential ones unimplemented)
	#but is by default the most recent *daily* leaderboard update available for default sorts
	#and the most recent leaderboard update (auto or manual) for non-default sorts

	if (not sort_type or (sort_type == "platinum" and file_name == "medals")) and not ytd:
		#if we're loading the most recent file of a default sort, just pull the cached csv
		latest = open("leaderboards/"+file_name+".csv", "r+")
		result = load_leaderboard(latest)
	elif ytd: #load most recent update from previous year to get gains made in this year
		#ytd does not support non-default sorts, as we don't guarantee a year-end scrape for those
		#if someone requests a ytd non-default sort it will error if no update exists for the prior year
		#and will just give over-estimatated results if an update did exist
		#(since the latest update from the previous year was likely well before year end)
		req_year = int(datetime.now().strftime('%Y')) - 1 #one before current year
		#build a list of all files from the requested year
		location = "leaderboards/archive/"+file_name+"/"
		req_file = get_file_by_year(req_year, location)
		if not req_file:
			return False
		last_year = open(location+req_file, "r+")
		result = load_leaderboard(last_year)
	elif sort_type:
		location = "leaderboards/archive/"+file_name+"/"
		req_file = get_file_by_sort(sort_type, location)
		if not req_file:
			return False
		last_file = open(location+req_file, "r+")
		result = load_leaderboard(last_file)

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
