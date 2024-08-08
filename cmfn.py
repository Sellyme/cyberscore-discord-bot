import math, os

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