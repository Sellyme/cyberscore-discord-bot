import math, os, datetime

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

def get_file_by_year(year, dir):
	#takes an input year, and finds the *most recent* file in a directory matching that year
	#this assumes all files in the directory have their yyyy-mm-dd timestamp as a filename prefix
	year = str(year)
	files = []
	
	for filename in os.listdir(dir):
		if filename.startswith(year):
			files.append(filename)
	
	#if there's no files, error out
	if len(files) == 0:
		print("ERROR: no files found in dir '" + dir + "' matching requested year '" + year + "'")
		return False
	
	#sort all the files and take the last alphabetically (which will be the closest to the end of year)
	req_file = sorted(files, reverse=True)[0]
	print("DEBUG: pulling file ", req_file)
	return req_file

def get_scoreboard_names(type, sortParam = 0):
	#takes in a consistent human-readable name of a specific scoreboard, and an optional sort poram
	#returns an array containing the name used as the site's URL for that board,
	#the name used for the filesystem where archives are stored, and the sort parameter name
	
	#set defaults
	site_name = type.lower()
	file_name = type.lower()
	sortType = ""
	
	#handle custom sortParams, and override for any name mismatches
	if type == "Medal":
		site_name = "medal"
		file_name = "medals"
		if sortParam == 1:
			sortType = "gold"
		elif sortParam == 2:
			sortType = "silver"
		elif sortParam == 3:
			sortType = "bronze"
	elif type == "Trophy":
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
	elif type == "Level":
		site_name = "incremental"
		sortType = "cxp"
	elif type == "Video":
		site_name = "vproof"
		file_name = "vproof"
	
	#and return the results
	return [site_name, file_name, sortType]

def get_leaderboard_from_disk(location, ytd = False):
	#parses and returns a leaderboard of the specified type from a certain date
	#date can be specified by optional parameters (many potential ones unimplemented)
	#but is by default the most recent *daily* leaderboard update available
	
	
	#if the ytd flag is set, load the *final* update from the previous calendar year
	if ytd:
		#get current year and subtract one
		req_year = int(datetime.now().strftime('%Y')) - 1
		#build a list of all files from the requested year
		req_file = cmfn.get_file_by_year(req_year, location)
		if not req_file:
			return False
		last_year = open(location+req_file, "r+")
		result = load_leaderboard(last_year)
	else: #otherwise, load the most recently saved file
		result = load_leaderboard(f)
	
	return result

def scrape_leaderboard_new(): #rename when done
	#todo - reimplement all of the leaderboard scraping here
	#and instead of building a string, build a rich datastructure
	#that we can then use to output differently-sorted results
	#(e.g., order a CSR leaderboard by gains instead of total)
	return False