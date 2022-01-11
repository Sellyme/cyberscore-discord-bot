import requests
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://cyberscore.me.uk/latest_subs.php"
CS_PREFIX = "https://cyberscore.me.uk"
last_update_time = 0 #todo - set this to startup or a saved time

def scrape():
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
		#col 5 is the star image
		pos_col = columns[6]
		#col 7 is the chart type image
		award_col = columns[8]
		#col 9 is empty

		country = flag_col.img.get('alt')
		#handle unknown locations
		if country == "--":
			flag_emoji = ":pirate_flag:"
		else:
			flag_emoji = ":flag_" + country.lower() + ":"
		
		name = name_col.a.get_text()
		game_name = game_col.strong.get_text()
		game_link = game_col.a['href']
		game = "["+game_name+"]("+CS_PREFIX+game_link+")"
		
		chart_links = list(chart_col.find_all('a'))
		group_name = chart_links[0].get_text()
		chart_name = chart_links[1].get_text()
		chart_link = chart_col.find_all('a')[1]['href']
		chart = "["+group_name + " → " + chart_name+"]("+CS_PREFIX+chart_link+")"
		
		score = score_col.a.get_text()
		pos = pos_col.get_text().replace(" ","")
		csr = award_col.strong
		#csr is not displayed for UC charts, so display Challenge Points instead
		if csr:
			csr = csr.get_text().strip()
		else:
			csr = award_col.span.get_text()

		#construct string
		output = flag_emoji + " " + name + " just scored " + score + " on " + game + "\n"
		output += chart + "\n"
		output += "Position: " + pos + " ("+csr+")"
		
		results.append(output)

	#once we've iterated over everything we can save the last update date
	if(new_update > last_update):
		f.seek(0)
		f.write(new_update)
		f.truncate()
	else:
		now = datetime.now()
		print(now.strftime("%H:%M:%S"), "no updates")
	f.close()
	
	return results
