import requests, re, json, csv, math
import cmfn #common functions

pokemon_templates = {}
pokemon_forms_by_id = {}
pokemon_forms_by_name = {}

def get_game_master():
	print("Loading game master")
	URL = "https://raw.githubusercontent.com/PokeMiners/game_masters/master/latest/latest.json"
	page = requests.get(URL)
	gm = json.loads(page.content)

	for template in gm:
		template_name = template['templateId']
		
		#build form database
		template_regex = r'FORMS_V(\d\d\d\d)_POKEMON_(.*)'
		m = re.fullmatch(template_regex, template_name)
		if m:
			pokemon_id = m.group(1)
			pokemon_name = m.group(2)
			
			#Nidoran needs special handling, as two Pokemon have that name
			if pokemon_name == "NIDORAN":
				if pokemon_id == "0029":
					pokemon_name = "NIDORAN_F"
				elif pokemon_id == "0032":
					pokemon_name = "NIDORAN_M"
			
			#print("Processing", pokemon_name, pokemon_id)
			form_list = []
			formSettings = template['data']['formSettings']
			if 'forms' in formSettings and formSettings['forms'][0] != {}:
				#if this Pokemon has a form list, iterate through them all
				for form in formSettings['forms']:
					if 'isCostume' in form and form['isCostume']:
						#ignore costume mons
						continue
					elif "COPY_2019" in form['form'] :
						#also ignore 2019 clone pokemon, which aren't tagged costume
						continue
					else:
						form_list.append(form['form'])
			else:
				form_list.append(formSettings['pokemon'])
			
			pokemon_forms_by_id[pokemon_id] = form_list
			pokemon_forms_by_name[pokemon_name] = form_list
		
		#hardcode in Nidoran (and any other common mistakes?) for !forms handling
		pokemon_forms_by_name["NIDORAN"] = ["NIDORAN_F", "NIDORAN_M"]
		pokemon_forms_by_id["0029"] = ["NIDORAN_F"]
		pokemon_forms_by_id["0032"] = ["NIDORAN_M"]
		pokemon_forms_by_name["UNOWN"] = ["UNOWN"]
		pokemon_forms_by_id["0201"] = ["UNOWN"]
		
		template_regex = r'^V(\d\d\d\d)_POKEMON_(.*)'

		m = re.fullmatch(template_regex, template_name)
		if m:
			pokemon_id = m.group(1)
			pokemon_name = m.group(2)

			if pokemon_name == "NIDORAN":
				if pokemon_id == "0029":
					pokemon_name = "NIDORAN_F"
				elif pokemon_id == "0032":
					pokemon_name = "NIDORAN_M"

			if pokemon_name in pokemon_forms_by_id[pokemon_id]:
				pokemon_templates[pokemon_name] = template

	print(pokemon_forms_by_name)
	print("Game master loaded")

def get_forms(mon, type): #type is either "name" or "number"
	if mon == "0029" or mon == "0032" or mon.startswith("NIDORAN"):
		return pokemon_forms_by_name["NIDORAN"]
	elif type == "number" and mon in pokemon_forms_by_id:
		return pokemon_forms_by_id[mon]
	elif type == "name" and mon in pokemon_forms_by_name:
		return pokemon_forms_by_name[mon]

	return False #if no match was found

#POKEMON STATISTIC GETTERS, ORDERED BY POSITION IN GAME MASTER
def get_type(mon):
	template = get_template(mon)
	type = template['data']['pokemonSettings']['type'].removeprefix("POKEMON_TYPE_")
	output = type.title()

	if "type2" in template['data']['pokemonSettings']:
		type2 = template['data']['pokemonSettings']['type2'].removeprefix("POKEMON_TYPE_")
		output += "/"+type2.title()

	return output

def get_bcr(mon):
	template = get_template(mon)
	bcr = template['data']['pokemonSettings']['encounter']['baseCaptureRate']
	return str(bcr)

def get_stats(mon):
	template = get_template(mon)
	stats = template['data']['pokemonSettings']['stats']
	output = "Atk "+str(stats['baseAttack'])
	output += " / Def "+str(stats['baseDefense'])
	output += " / HP "+str(stats['baseStamina'])
	return output

def get_moves(mon):
	template = get_template(mon)
	f_moves = template['data']['pokemonSettings']['quickMoves']
	#for lists we want the first line to be a header so that it looks pretty in compact mode
	output = "Moves for Pokemon '"+mon+"'\n"
	output += "FAST\n"
	for move in f_moves:
		#turn "FURY_CUTTER_FAST" into "Fury Cutter"
		output += move.removesuffix("_FAST").replace("_"," ").title()+"\n"
	
	#separate fast and charge blocks
	output += "\nCHARGE\n"
	c_moves = template['data']['pokemonSettings']['cinematicMoves']
	for move in c_moves:
		output += move.replace("_"," ").title()+"\n"
	
	return output

def get_dex_weight(mon):
	template = get_template(mon)
	if template:
		weight = template['data']['pokemonSettings']['pokedexWeightKg']
		return weight
	else:
		return False

def get_dex_height(mon):
	template = get_template(mon)
	if template:
		height = template['data']['pokemonSettings']['pokedexHeightM']
		return height
	else:
		return False

#returns an array containing two elements:
#first element is either negative (lowest wins) or positive (highest wins)
#second element is an array of chances (where 0.50 == 50%)
#if the array contains just one value, that's the chance for any wild spawn
#if the array contains three values, they're the chances for class one through three species respectively
def get_height_chance(mon, height):
	#height ranges for reference:
	#note that a Pokemon species can only be in ONE XXL group, either XXL1, XXL2, or XXL3
	#the chance displayed for each of those groups in this list assumes that the species IS in that group
	#XXS Smallest: 0.49 - 0.492 (1/250 chance XXS * 1/20 chance Smallest)
	#XXS Normal: 0.492 - 0.50 (1/250 chance XXS * 19/20 chance not Smallest)
	#XS: 0.50 - 0.75 (1/40 chance)
	#AVG: 0.75 - 1.25 (471/500 chance [100% - 1/250*2 - 1/40*2])
	#XL: 1.25 - 1.50 (1/40 chance)
	#XXL1 Normal: 1.50 - 1.54 (1/250 chance XXL * 19/20 chance not Largest)
	#XXL1 Largest: 1.54 - 1.55 (1/250 chance XXL * 1/20 chance Largest)
	#XXL2 Normal: 1.50 - 1.70 (1/250 chance XXL * 19/20 chance not Largest)
	#XXL2 Largest: 1.70 - 1.75 (1/250 chance XXL * 1/20 chance Largest)
	#XXL3 Normal: 1.50 - 1.90 (1/250 chance XXL * 19/20 chance not Largest)
	#XXL3 Largest: 1.90 - 2.00 (1/250 chance XXL * 1/20 chance Largest)
	#Note that in the actual code we halve all of these values because we look at <avg and >avg separately
	#A 1/250 chance of XXS becomes 1/125 when you're only considering sizes below average

	#print("Height", height)
	dex_height = get_dex_height(mon)
	#print("Dex height", dex_height)
	height_variate = height / dex_height
	win_chance = 0

	if height_variate < 1.00:
		category = -1
		
		#check what the winning score will be - if close to boundaries this can behave oddly
		#todo - this solution is naive and doesn't handle non-contiguous "win" ranges that can occur
		#at the upper border for XS (0.75x). Fortunately, for the use case of this bot, the 0.75x range
		#isn't as relevant, we're more interested in the XXS range.
		#Note that despite 4 statements here, there's only two different behaviours on our end.
		#This is just to more explicitly state each case, even though the end result is the same
		#and hopefully aid with debugging.
		if int(dex_height*100) % 2 == 0 and round(height*100) == round(dex_height*100/2):
			#this height is the minimum possible XS, and any XXS will beat it due to rounding
			#so winning_score is anything even 0.00001 better than set score
			winning_score = height
		elif int(dex_height*100) % 2 == 1 and round(height*100) == math.ceil(dex_height*100/2):
			#this is a Pokemon where the XS boundary is e.g., 0.495m
			#the score to beat is [0.495,0.50) (aka, XS), and any XXS will beat it
			#so winning score is anything <0.005 lower
			winning_score = height - 0.005
		elif int(dex_height*100) % 2 == 1 and round(height*100) == math.floor(dex_height*100/2):
			#same species case as previous, but the score to beat is [0.490,0.495), and displays as 0.49.
			#any score lower than 0.49 will be within 0.01 of the height boundary, and therefore floors
			#meaning any score below the displayed score (the height var) will beat it
			winning_score = height
		else:
			#default handling if no weird class boundary behaviour exists
			winning_score = height - 0.005

		winning_variate = winning_score / dex_height
		
		print("Winning variate to beat",winning_score,"is",winning_variate)
		if winning_variate <= 0.49:
			return [category, [win_chance]] #scores this low are not possible

		#xxs low range
		win_chance += min(max(0, winning_variate - 0.49), 0.002) / 250 / 20 / 0.002
		
		if winning_variate > 0.492: #xxs high range
			win_chance += min(winning_variate - 0.492, 0.008) / 250 / 20 * 19 / 0.008
		if winning_variate > 0.50: #xs
			win_chance += min(winning_variate - 0.50, 0.25) / 40 / 0.25
		if winning_variate > 0.75: #avg
			win_chance += (winning_variate - 0.75) / 500 * 471 / 0.500
		
		return [category, [win_chance]]

	else: #for heights exactly 1.00 it doesn't matter in what direction we look, so look for higher
		category = 1
		winning_score = height + 0.005
		winning_variate = winning_score / dex_height
		if winning_variate >= 2.00:
			return [category, [win_chance]] #scores this high are not possible
		
		#first, assume that the Pokemon is NOT XXL, to get the simple maths out of the way
		if winning_variate < 1.50: #xl
			win_chance += min(1.50 - winning_variate, 0.25) / 40 / 0.25
		if winning_variate < 1.25: #avg
			win_chance += (1.25 - winning_variate) / 500 * 471 / 0.500
		
		#finally, calculate all three possible XXL classes on top of the base stats
		win_chances = [win_chance, win_chance, win_chance]

		#XXL1
		win_chances[0] += min(max(0, 1.55 - winning_variate), 0.01) / 250 / 20 / 0.01
		if winning_variate < 1.54:
			win_chances[0] += min(1.54 - winning_variate, 0.04) / 250 / 20 * 19 / 0.04
		#XXL2
		win_chances[1] += min(max(0, 1.75 - winning_variate), 0.05) / 250 / 20 / 0.05
		if winning_variate < 1.70:
			win_chances[1] += min(1.70 - winning_variate, 0.20) / 250 / 20 * 19 / 0.20
		#XXL3
		win_chances[2] += min(max(0, 2.00 - winning_variate), 0.10) / 250 / 20 / 0.10
		if winning_variate < 1.90:
			win_chances[2] += min(1.90 - winning_variate, 0.40) / 250 / 20 * 19 / 0.40

		return [category, win_chances]

def get_weight_chance(mon, weight):
	win_chances = [0, 0, 0]

	dex_weight = get_dex_weight(mon)
	if not dex_weight:
		return False

	weight_variate = weight / dex_weight
	if weight_variate < 1.00:
		category = -1
		winning_score = weight - 0.005
		winning_variate = math.floor(winning_score / dex_weight * 10000) / 10000
		if winning_variate <= 0:
			return [category, win_chances]
	else:
		category = 1
		winning_score = weight + 0.005
		winning_variate = math.ceil(winning_score / dex_weight * 10000) / 10000
		if winning_variate >= 2.75:
			return [category, win_chances]

	cdf_files = [
		'pokemon_cdfs/cdf_155.txt',
		'pokemon_cdfs/cdf_175.txt',
		'pokemon_cdfs/cdf_200.txt',
	]
	
	#line number we're targeting will be 1 higher than the variate * 10k
	line_num = int(winning_variate * 10000) + 1
	#for highest wins, the chance is now 1 - line[2]
	#for lowest wins, the chance is line[2]

	for i in range(0,3):
		cdf_file = cdf_files[i]
		with open(cdf_file, 'r', encoding='utf8') as cdf:
			tsv_reader = csv.DictReader(cdf, delimiter="\t")
			rows = list(tsv_reader)
			if category == -1:
				win_chances[i] = float(rows[line_num]['cumChance'])
			else:
				win_chances[i] = 1 - float(rows[line_num]['cumChance'])
	
	return [category, win_chances]

#formats a pokemon name the way the game master stores them
#with special characters either converted to ASCII (é→e) or stripped (:),
#spaces converted to underscores, and all characters capitalised
def format_name(name):
	#replace all spaces with underscores: "tapu koko" → "TAPU_KOKO"; "JANGMO-O" → "JANGMOO"
	name = name.upper().replace(" ","_").replace("-","_").replace("é","e").replace("É","E").replace("♀","F").replace("♂","M")
	for char in ":'’.": #strip special chars: "FARFETCH'D" → "FARFETCHD"; "MR._MIME" → "MR_MIME"
		if char in name:
			name = name.replace(char, "")
	return name

def get_template(mon): #mon is always a name of format DARUMAKA_GALAR
	#handle any conversions directly from CS chart names
	if "(" in mon:
		#pull out the mon name, and put the form info in a second entry
		mon_chunks = mon.split("_(")
		#and then check all the form types and reconstruct string
		if mon_chunks[1] == "ALOLAN_FORM)":
			mon = mon_chunks[0] + "_ALOLA"
		elif mon_chunks[1] == "GALARIAN_FORM)":
			mon = mon_chunks[0] + "_GALARIAN"
		elif mon_chunks[1] == "HISUIAN_FORM)":
			mon = mon_chunks[0] + "_HISUIAN"
		elif mon_chunks[0] == "FRILLISH" or mon_chunks[0] == "PYROAR" or mon_chunks[0] == "Meowstic":
		#Pokemon where user display is Male/Female, but game master is Normal/Female (lmao wtf)
			mon = mon_chunks[0]+"_"+mon_chunks[1].replace(")","").replace("MALE","NORMAL")
		else:
		#Pokemon with "Pokemon (Form)" names. In many cases the form has a suffix, which we strip.
			mon = mon_chunks[0]+"_"+mon_chunks[1].replace(")","").replace("_FORME","").replace("_CLOAK","").replace("_FORM","").replace("_DRIVE","").replace("_FLOWER","").replace("_TRIM","").replace("_SIZE","").replace("_STYLE","").replace("POM_POM","POMPOM")
			#note the "POMPOM" special case for Oricorio
			#this is the only Pokemon where the game master strips "-" instead of replacing with "_"

	#print("Searching template for", mon)
	#handle Nidoran
	if mon == "NIDORANF" or mon == "NIDORAN_F":
		return pokemon_templates["NIDORAN_F"]
	elif mon == "NIDORANM" or mon == "NIDORAN_M":
		return pokemon_templates["NIDORAN_M"]

	if mon in pokemon_templates:
		#print("Found, returning")
		return pokemon_templates[mon]
	elif mon+"_NORMAL" in pokemon_templates:
		#print("Found (Normal), returning")
		return pokemon_templates[mon+"_NORMAL"]
	elif mon == "SPINDA":
	#we don't care about Spinda forms being separate, so just take any of them
		return pokemon_templates["SPINDA_00"]
	elif mon == "SCATTERBUG":
	#same for Scatterbug
		return pokemon_templates["SCATTERBUG_ARCHIPELAGO"]
	else:
		print("Couldn't find template for",mon)
		return False

def analyse_score(score):
	#get Pokemon from the chart name
	#todo - need to handle form names specially here
	mon = format_name(score['chart'][8:])
	print("Analysing mon: ",mon)

	size_set = score['score']
	#we need to offset the scores by the rounding margin used to calculate win chances
	#in order to get the chances of *setting* that score, rather than the chances of *beating* it
	#score['polarity'] is 0 for low, 1 for high
	if score['polarity'] == 0:
		size_beaten = score['score'] + 0.01
	elif score['polarity'] == 1:
		size_beaten = score['score'] - 0.01

	#score['type'] is 0 for weight, 1 for height
	#note that get_*eight_chance returns a list of two variables
	#idx 0 is -1 if lower is better, +1 if higher is better. We can ignore that.
	#idx 1 is the list of win chances depending on species class. This is what we want
	if score['type'] == 0:
		chance_to_set = get_weight_chance(mon, size_beaten)[1]
		chance_to_beat = get_weight_chance(mon, size_set)[1]
	elif score['type'] == 1:
		chance_to_set = get_height_chance(mon, size_beaten)[1]
		chance_to_beat = get_height_chance(mon, size_set)[1]

	print(chance_to_set)
	#normalise the chances into a single value
	#for now we just take the maximum value, so we never have any false positives
	#in the future we should try to build a DB of what XXL class each species is in and pull the correct one
	if len(chance_to_set) > 1:
		chance_to_set = [max(chance_to_set)]
	if len(chance_to_beat) > 1:
		chance_to_beat = [max(chance_to_beat)]
	chance_to_set = chance_to_set[0]
	chance_to_beat = chance_to_beat[0]

	#construct string
	if chance_to_beat == 0:
		output = "**New perfect score!**\n" #replace with "New perfect score" or "New rare score" accordingly
	elif chance_to_set < 0.001:
		output = "**New rare score!**\n"
	else:
		return None

	#if we get here an output is desired

	#then start building the string
	output += score['flag_emoji'] + " " + score['user_link'] + " just scored " + score['score_link'] + "\n"
	output += score['game'] + " → " + score['chart_link'] + "\n"
	#first, generate the numbers indicating rarity
	#we check that this is >0 first to avoid reporting incorrect data for XXS heights (see below)
	if chance_to_set > 0:
		perc = str(round(chance_to_set * 100,3))
		frac = str(round(1/chance_to_set))
		output += "This score was a " +perc+"% chance of occurring (1 in "+frac+")"
	else:
		output += "This score appears to be impossible. If it's definitely correct, yell at <@101709643822157824> to fix his code."

	return output