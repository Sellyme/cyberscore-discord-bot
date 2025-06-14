import csv
import json
import math
import re
from os import listdir
from os.path import isfile, join

import requests
from clrprint import clrprint

import config

pokemon_templates = {}
pokemon_forms_by_id = {}
pokemon_forms_by_name = {}
pokemon_class_boundaries = {}
processed_charts = {"Lightest": {}, "Heaviest": {}, "Shortest": {}, "Tallest": {}}

def get_game_master():
	print("Loading game master")
	URL = "https://raw.githubusercontent.com/PokeMiners/game_masters/master/latest/latest.json"
	page = requests.get(URL, timeout=config.timeout)
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
					if not isinstance(form['form'], str):
						print("Error: Invalid form",form['form'],"found for",pokemon_name)

						#Falinks' base form appears to error out due to being an integer, so correct that
						if form['form'] == 2325 and pokemon_name == "FALINKS":
							form_list.append("FALINKS")
						else:
							continue
					elif 'isCostume' in form and form['isCostume']:
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
			#print("Loaded forms for", pokemon_name) #DEBUG

		#hardcode in Nidoran (and any other common mistakes?) for !forms handling
		pokemon_forms_by_name["NIDORAN"] = ["NIDORAN_F", "NIDORAN_M"]
		pokemon_forms_by_id["0029"] = ["NIDORAN_F"]
		pokemon_forms_by_id["0032"] = ["NIDORAN_M"]
		pokemon_forms_by_name["UNOWN"] = ["UNOWN"]
		pokemon_forms_by_id["0201"] = ["UNOWN"]
		pokemon_forms_by_name["SPINDA"] = ["SPINDA"]
		pokemon_forms_by_id["0327"] = ["SPINDA"]

		#build template list
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
				#print("Loaded template for", pokemon_name) #DEBUG

	print("Templates built. Loading sizes")
	#we've built the template list, now we do another loop to add extended size data
	#we can't do this in the main loop because it comes before the templates in the gm
	#ideally we'd just save these to memory in the first iteration and come back to them (TODO)
	for template in gm:
		template_name = template['templateId']
		#Pull out size class boundaries
		template_regex = r'^EXTENDED_V(\d\d\d\d)_POKEMON_(.*)'
		m = re.fullmatch(template_regex, template_name)
		if m:
			pokemon_id = m.group(1)
			pokemon_name = m.group(2)

			#hardcode Nidoran genders + some weird mons that aren't stored consistently
			if pokemon_name == "NIDORAN":
				if pokemon_id == "0029":
					pokemon_name = "NIDORAN_F"
				elif pokemon_id == "0032":
					pokemon_name = "NIDORAN_M"

			gm_sizes = template['data']['pokemonExtendedSettings']['sizeSettings']
			#print("Loaded sizes for", pokemon_name) #DEBUG
			if pokemon_name in pokemon_templates:
				pokemon_templates[pokemon_name]['sizeclasses'] = convert_gm_sizes(gm_sizes)
			else:
				#some mons have inconsistent game master data, and we need to manually correct them
				#hopefully these snippets are written such that if this is ever fixed, they never get reached
				if pokemon_name == "BEARTIC":
					#this is actually wrong, Beartic size generation is just broken in the game
					#this gives the numbers that SHOULD happen, but they don't in practice.
					#it's likely defaulting to the old height/weight system instead
					pokemon_templates["BEARTIC_NORMAL"]['sizeclasses'] = convert_gm_sizes(gm_sizes)
				elif pokemon_name == "AVALUGG":
					#Hisuian Avalugg and Kalos Avalugg both use the same size data?? wtf are you doing niantic
					classes = convert_gm_sizes(gm_sizes)
					pokemon_templates["AVALUGG_HISUIAN"]['sizeclasses'] = classes
					pokemon_templates["AVALUGG_NORMAL"]['sizeclasses'] = classes
				elif pokemon_name+"_NORMAL" in pokemon_templates:
					#we use e.g., "BULBASAUR_NORMAL" instead of "BULBASAUR" when both exist
					#in cases where both names exist we can just ignore the latter
					#note that we do need to periodically manually check for errors like Beartic
					#where both templates exist but only the latter has size data
					continue
		#else:
		#loads of stuff in here is costume forms or things like Giratina
		#where there's "GIRATINA" but all actual mons are "GIRATINA_ORIGIN" or "GIRATINA_ALTERED"
		#may be worth enabling the debug and sanity-checking it periodically though
		#print("Error: Found size data for Pokemon",pokemon_name,"but could not match it to a template")

	#print(pokemon_forms_by_name)
	print("Game master loaded")

def convert_gm_sizes(obPokemonSizeSettings):
	classes = []
	for item in obPokemonSizeSettings:
		classes.append(obPokemonSizeSettings[item])
	return classes

def get_forms(mon, search_type): #search_type is either "name" or "number"
	if mon == "0029" or mon == "0032" or mon.startswith("NIDORAN"):
		return pokemon_forms_by_name["NIDORAN"]
	elif search_type == "number" and mon in pokemon_forms_by_id:
		return pokemon_forms_by_id[mon]
	elif search_type == "name" and mon in pokemon_forms_by_name:
		return pokemon_forms_by_name[mon]

	return False #if no match was found

#POKEMON STATISTIC GETTERS, ORDERED BY POSITION IN GAME MASTER
def get_type(mon):
	template = get_template(mon)
	pokemon_type = template['data']['pokemonSettings']['type'].removeprefix("POKEMON_TYPE_")
	output = pokemon_type.title()

	if "type2" in template['data']['pokemonSettings']:
		type2 = template['data']['pokemonSettings']['type2'].removeprefix("POKEMON_TYPE_")
		output += "/"+type2.title()

	return output

#deprecated, no longer available in gm
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
	#for lists, we want the first line to be a header so that it looks pretty in compact mode
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
		#why the hell do I need to hardcode so many fixes for Niantic's incompetence
		if template['templateId'] == "V0194_POKEMON_WOOPER_PALDEA":
			weight = 11.0
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

def get_dex_heights(mon):
	bounds = get_class_boundaries(mon)


#takes in a height from the game master and calculates the variate for that mon, rounding off fp errors
def rounded_variate(height, dex_height):
	return round(height/dex_height,5)

#returns an array of [dex_height, [class1, class2, class3, etc]]
#where class1...6 represent the (overlapping) lower and upper boundaries of each class
def get_class_boundaries(mon):
	height = get_dex_height(mon)
	#H-Avalugg is still VERY broken and doesn't have any actual data available
	#right now the K-Avalugg data is being inserted into its template during gm loading
	#so to make that workable, for the calculations we'll hardcode K-Avalugg's dex height
	#and assume that H-Avalugg actually has all the same class boundaries
	#this could be incorrect, but it's at least less incorrect than calculating them with the wrong heights
	avalugg_flag = False
	real_height = None
	if "AVALUGG" in mon.upper() and "HISUI" in mon.upper():
		avalugg_flag = True
		real_height = height
		height = get_dex_height("AVALUGG")

	template = get_template(mon)
	if template:
		classes = template['sizeclasses']
		xxs_low = rounded_variate(classes[0], height)
		xs_low = rounded_variate(classes[1], height)
		xs_high = rounded_variate(classes[2], height)
		xl_low = rounded_variate(classes[3], height)
		xxl_low = rounded_variate(classes[4], height)
		xxl_high = rounded_variate(classes[5], height)
		#clean up the disgusting Avalugg mangling we just did
		if avalugg_flag:
			height = real_height
		#and return output
		return [height, [xxs_low, xs_low, xs_high, xl_low, xxl_low, xxl_high]]
	else:
		return False

#formats get_class_boundaries to be human-readable for use in command line
def get_bounds(mon):
	mon = format_name(mon)
	bounds = get_class_boundaries(mon)

	output = "```\n"
	max_height = bounds[0]*bounds[1][5]
	max_height_length = len(format_size(max_height))
	cell_width = max_height_length
	#if cell-width is even, the headers look like shit
	if cell_width % 2 == 0:
		cell_width += 1

	#The box comprises 6 columns
	#The first column is for labels and contains either " Heights " or " Weights " (9 chars)
	#Each subsequent column is "|" followed by a cell of cell_width size
	#We don't count the outer |s since we manually print corners anyway
	box_width = 9 + (5 * (cell_width+1))
	output += "┏" + "━"*box_width + "┓\n"

	#print box header
	header = "Heights for " + mon
	h_spaces = (box_width - len(header)) / 2
	#we round h_spaces down for the leading spaces and then up for the second
	#this way if it wasn't an integer, the extra space is always trailing
	output += "┃" + " "*math.floor(h_spaces) + header + " "*math.ceil(h_spaces) + "┃\n"
	output += "┣" + "━"*9 #start of header lower border
	output += 5*("┳" + "━"*cell_width) + "┫\n"

	#print class headers
	output += "┃" + 9*" " + "┃"
	c_spaces = " "*int((cell_width - 3) / 2) #this is always an integer even before the cast
	output += c_spaces + "MIN" + c_spaces + "┃"
	output += c_spaces + "XXS" + c_spaces + "┃"
	output += c_spaces + "DEX" + c_spaces + "┃"
	output += c_spaces + "XXL" + c_spaces + "┃"
	output += c_spaces + "MAX" + c_spaces + "┃\n"

	#print Heights row
	output += "┃ Heights "
	#MIN
	if((bounds[0]*bounds[1][1]) - (bounds[0]*bounds[1][0]) < 0.01):
		true_min = math.floor(bounds[0]*bounds[1][0]*100) / 100.0
	else:
		#round it very mildly to clear accrued floating point errors rounding properly to 1cm
		true_min = round(round(bounds[0]*bounds[1][0], 6),2)
	output += create_size_cell(true_min, cell_width)
	#XXS
	output += create_size_cell(bounds[0]*bounds[1][1], cell_width)
	#DEX
	output += create_size_cell(bounds[0], cell_width)
	#XXL
	output += create_size_cell(bounds[0]*bounds[1][4], cell_width)
	#MAX
	output += create_size_cell(max_height, cell_width)
	output += "┃\n"

	output += "┃ Odds    "
	min_odds = get_height_chance(mon, true_min+0.01)
	output += create_odds_cell(min_odds[1], cell_width)
	output += create_odds_cell(1/250, cell_width)
	output += create_odds_cell(False, cell_width)
	output += create_odds_cell(1/250, cell_width)
	max_odds = get_height_chance(mon, bounds[0]*bounds[1][5] - 0.01)
	output += create_odds_cell(max_odds[1], cell_width)
	output += "┃\n"
	#footer
	output += "┗" + "━"*9
	output += 5*("┻" + "━"*cell_width) + "┛\n"
	output += "```"

	print("XXL class: %.2f" % (bounds[1][5]))
	print("XXS Min: %.4f" % (bounds[0]*bounds[1][0]))
	print("XXS Max: %.4f" % (bounds[0]*bounds[1][1]))
	print("DEX: %.2f" % bounds[0])
	print("XXL Min: %.4f" % (bounds[0]*bounds[1][4]))
	print("XXL Max: %.4f" % (bounds[0]*bounds[1][5]))

	return output

def create_size_cell(size_float, cell_width):
	size_str = format_size(size_float)
	return "┃" + " "*(cell_width - len(size_str)) + size_str

def format_size(size_float):
	return f'{size_float:.2f}m '

def create_odds_cell(odds_float, cell_width):
	if odds_float:
		odds_str = format_odds(odds_float)
	else:
		odds_str = "—"
	spaces_req = (cell_width - len(odds_str)) / 2.0
	return "┃" + " "*math.ceil(spaces_req) + odds_str + " "*math.floor(spaces_req)

def format_odds(odds_float):
	#odds float is a number between 0.00 and 1.00
	frac = 1/odds_float

	magnitude = 0
	while frac >= 1000:
		magnitude += 1
		frac /= 1000.0
	#if frac is <10 we want to print e.g., 2.6
	#if it's >=10 we want just 26 or 273
	if frac < 10:
		dec = 1
	else:
		dec = 0

	if magnitude > 5:
		#this means less than 1 in 1000 quadrillion
		return "LOTS"

	f_str = '1/{:.'+str(dec)+'f}{} '
	return f_str.format(frac, ['', 'k', 'm', 'b', 't', 'q'][magnitude])

#returns an array containing two elements:
#first element is either negative (lowest wins) or positive (highest wins)
#second element is an array of chances (where 0.50 == 50%)
#if the array contains just one value, that's the chance for any wild spawn
#if the array contains three values, they're the chances for class one through three species respectively
def get_height_chance(mon, height):
	#print("Checking height chance for",mon,"with height",height)
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

	#Also note that Scatterbug's XXS class boundaries do not match every other species'
	#and range from 0.25x to 0.50x.
	#It appears that the same split occurs where the bottom 20% of this range only covers 5% of XXS spawns

	height_data = get_class_boundaries(mon)
	if not height_data:
		return False

	dex_height = height_data[0]
	classes = height_data[1]
	#build class widths
	xxs_width = classes[1] - classes[0]
	xxs_small_width = xxs_width/5
	xxs_big_width = xxs_width*4/5
	xs_width = classes[2] - classes[1]
	avg_width = classes[3] - classes[2]
	xl_width = classes[4] - classes[3]
	xxl_width = classes[5] - classes[4]
	xxl_small_width = xxl_width*4/5
	xxl_big_width = xxl_width/5

	height_variate = height / dex_height
	win_chance = 0

	if height_variate < 1.00:
		category = -1

		#todo - replace all of this with a very simple check against one step up in classes
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

		if winning_variate <= classes[0]:
			return [category, win_chance] #scores this low are not possible, so return the default 0

		#xxs low range
		win_chance += min(max(0, winning_variate - classes[0]), xxs_small_width) / 250 / 20 / xxs_small_width
		if winning_variate > (classes[0]+xxs_small_width): #xxs high range
			win_chance += min(winning_variate - (classes[0]+xxs_small_width), xxs_big_width) / 250 / 20 * 19 / xxs_big_width
		if winning_variate > 0.50: #xs
			win_chance += min(winning_variate - classes[1], xs_width) / 40 / xs_width
		if winning_variate > 0.75: #avg
			win_chance += (winning_variate - classes[2]) / 500 * 471 / avg_width

		return [category, win_chance]
	else: #for heights exactly 1.00 it doesn't matter in what direction we look, so look for higher
		category = 1
		winning_score = height + 0.005
		winning_variate = winning_score / dex_height
		if winning_variate >= classes[5]:
			return [category, win_chance] #scores this high are not possible, so return the default 0

		#first, assume that the Pokemon is NOT XXL, to get the simple maths out of the way
		if winning_variate < classes[4]: #xl
			win_chance += min(classes[4] - winning_variate, xl_width) / 40 / xl_width
		if winning_variate < classes[3]: #avg
			win_chance += (classes[3] - winning_variate) / 500 * 471 / avg_width

		#xxl low range
		if winning_variate < (classes[5] - xxl_big_width):
			win_chance += min((classes[5]-xxl_big_width) - winning_variate, xxl_small_width) / 250 / 20 * 19 / xxl_small_width
		#xxl high range
		win_chance += min(max(0, classes[5] - winning_variate), xxl_big_width) / 250 / 20 / xxl_big_width

		#and return the output
		#third output is xxl_known, which is now always true - TODO remove this
		return [category, win_chance]

def get_weight_chance(mon, weight):
	win_chance = 0
	height_data = get_class_boundaries(mon)
	if not height_data:
		return False
	dex_height = height_data[0]
	classes = height_data[1]

	dex_weight = get_dex_weight(mon)
	if not dex_weight:
		return False

	weight_variate = weight / dex_weight
	if weight_variate < 1.00:
		category = -1
		winning_score = weight - 0.005
		winning_variate = winning_score / dex_weight
		if winning_variate <= 0:
			return [category, win_chance] #impossible to beat, return 0
	else:
		category = 1
		winning_score = weight + 0.005
		winning_variate = winning_score / dex_weight
		if winning_variate >= 2.75:
			return [category, win_chance] #impossible to beat, return 0

	cdf_files = [
		#todo - add a custom CDF for Scatterbug? Scatterbug weights will be incorrect with these
		'pokemon_cdfs/cdf_155.txt',
		'pokemon_cdfs/cdf_175.txt',
		'pokemon_cdfs/cdf_200.txt',
	]

	#line number we're targeting will be 1 higher than the variate * 10k
	win_var_10k = winning_variate * 10000
	float_line_num = win_var_10k % 1
	line_num = math.floor(win_var_10k)
	#for highest wins, the chance is now 1 - line[2]
	#for lowest wins, the chance is line[2]
	print("Winning variate:", winning_variate)
	#print("Line num:", line_num, float_line_num)

	if classes[5] == 1.55:
		cdf_idx = 0
	elif classes[5] == 1.75:
		cdf_idx = 1
	elif classes[5] == 2:
		cdf_idx = 2
	else:
		print("Error: XXL multiplier for",mon,"not valid; reporting",classes[5])
		return False

	with open(cdf_files[cdf_idx], 'r', encoding='utf8') as cdf:
		tsv_reader = csv.DictReader(cdf, delimiter="\t")
		rows = list(tsv_reader)
		if category == -1:
			win_chance = float(rows[line_num]['cumChance'])
			win_chance += (float(rows[line_num+1]['cumChance']) - win_chance) * float_line_num
		else:
			row_chance = float(rows[line_num]['cumChance'])
			win_chance = 1 - row_chance
			win_chance -= (float(rows[line_num+1]['cumChance']) - row_chance) * float_line_num

	return [category, win_chance]

#formats a pokemon name the way the game master stores them
#with special characters either converted to ASCII (é→e) or stripped (:),
#spaces converted to underscores, and all characters capitalised
def format_name(name):
	#start by checking for a shorthand regional form representation
	name = convert_regional_forms(name)
	#replace all spaces with underscores: "tapu koko" → "TAPU_KOKO"; "JANGMO-O" → "JANGMOO"
	name = name.upper().replace(" ","_").replace("-","_").replace("é","e").replace("É","E").replace("♀","F").replace("♂","M")
	for char in ":'’.": #strip special chars: "FARFETCH'D" → "FARFETCHD"; "MR._MIME" → "MR_MIME"
		if char in name:
			name = name.replace(char, "")
	return name

def convert_regional_forms(name):
	#takes in a name of the form "A-Sandshrew" and outputs it in the form "Sandshrew_Alola"
	#handling is all done case-insensitively, as format_name() handles capitalisation after this
	if name.startswith(("K-","k-")):
		#Kanto and Kalos have no regional forms that are specified by their region name
		#however many regional forms are forms of Pokemon that are Kanto by default (none for Kalos yet!)
		#so e.g., "K-Vulpix" may be used to explicitly specify Kanto Vulpix instead of Alolan Vulpix
		#but since we store that as simply "Vulpix", we can simply strip the prefix
		name = name.lstrip("k-").lstrip("K-")
	elif name.startswith(("A-","a-")):
		name = name.lstrip("A-").lstrip("a-")+"_ALOLA" #yes the inconsistencies with "ALOLA" v "ALOLAN" are dumb
	elif name.startswith(("G-","g-")):
		name = name.lstrip("G-").lstrip("g-")+"_GALARIAN"
	elif name.startswith(("H-","h-")):
		name = name.lstrip("H-").lstrip("h-")+"_HISUIAN"
	elif name.startswith(("P-","p-")):
		name = name.lstrip("P-").lstrip("p-")+"PALDEA"
	return name

#takes any formatted name, and then converts it into the exact name used in the pokemon_templates dict
#this is mostly just converting form names and handling edge cases like Nidoran
def get_template_name(mon):
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
		elif mon_chunks[1] == "PALDEAN_FORM)":
			mon = mon_chunks[0] + "_PALDEA"
		elif mon_chunks[0] == "FRILLISH" or mon_chunks[0] == "JELLICENT" or mon_chunks[0] == "PYROAR" or mon_chunks[0] == "MEOWSTIC" or mon_chunks[0] == "OINKOLOGNE":
			#Pokemon where user display is Male/Female, but game master is Normal/Female (lmao wtf)
			mon = mon_chunks[0]+"_"+mon_chunks[1]
			mon = mon.replace(")","").replace("_MALE","_NORMAL")
		elif mon_chunks[0] == "ZYGARDE":
			mon = mon_chunks[0]+"_"+mon_chunks[1]
			mon = mon.replace("%","_PERCENT").replace("10","TEN").replace("50","FIFTY").replace("_FORME)","")
		else:
			#Pokemon with "Pokemon (Form)" names. In many cases the form has a suffix, which we strip.
			mon_chunks[1] = mon_chunks[1].replace(")","").replace("_FORME","").replace("_CLOAK","").replace("_FORM","")
			mon_chunks[1] = mon_chunks[1].replace("_DRIVE","").replace("_FLOWER","").replace("_TRIM","").replace("_SIZE","")
			mon_chunks[1] = mon_chunks[1].replace("_STYLE","").replace("POM_POM","POMPOM").replace("SUNSHINE","SUNNY").replace("_MODE","")
			#note the "POMPOM" special case for Oricorio
			#this is the only Pokemon where the game master strips "-" instead of replacing with "_"
			#also note "Sunshine" (as shown in dex) being replaced with "Sunny" (as in GM) for Cherrim.
			mon = mon_chunks[0]+"_"+mon_chunks[1]

	#handle edge cases
	if mon == "NIDORANF" or mon == "NIDORAN_F":
		return "NIDORAN_F"
	elif mon == "NIDORANM" or mon == "NIDORAN_M":
		return "NIDORAN_M"
	elif mon == "ZACIAN":
		#zac/zam do not display form names in-game yet, but rely on them in gm
		return "ZACIAN_HERO"
	elif mon == "ZAMAZENTA":
		return "ZAMAZENTA_HERO"
	elif mon == "MORPEKO":
		#Morpeko Hangry is a form only available in battles, and is not important for CS purposes
		return "MORPEKO_FULL_BELLY"

	#handle Rotom, which is stored in GM as ROTOM_TYPE but in dex as "Type Rotom"
	if "ROTOM" in mon:
		mon_chunks = mon.split("_")
		if mon_chunks[0] == "ROTOM":
			return "ROTOM_NORMAL"
		else:
			return mon_chunks[1]+"_"+mon_chunks[0]

	if mon in pokemon_templates:
		#any simple matches can be returned verbatim
		#print("Found, returning")
		return mon
	elif mon+"_NORMAL" in pokemon_templates:
		#pokemon with shadow forms need the "_NORMAL" suffix
		#print("Found (Normal), returning")
		return mon+"_NORMAL"
	elif mon == "SCATTERBUG" or mon == "SPEWPA" or mon == "VIVILLON":
		#we don't care which Scatterbug form we return, so just pick any
		return mon+"_ARCHIPELAGO"
	elif mon == "DEERLING" or mon == "SAWSBUCK":
		#again, we don't care which form, so just get data for spring
		return mon+"_SPRING"
	elif mon == "FLABEBE" or mon == "FLOETTE" or mon == "FLORGES":
		#you know the drill
		return mon+"_ORANGE" #orange used because it's a global one and may help narrow down bugs if used relating to size scores
	else:
		print("Couldn't find template for",mon)
		return False

def get_template(mon): #mon is always a name of format DARUMAKA_GALAR
	template_name = get_template_name(mon)
	if template_name in pokemon_templates:
		return pokemon_templates[template_name]
	else:
		return None

def get_variates(mon, height, weight):
	mon = get_template_name(mon)

	#if mon name was incorrect, fail out
	if not mon:
		return None

	min_height = height-0.005
	max_height = height+0.005
	height_data = get_class_boundaries(mon)
	dex_height = height_data[0]
	classes = height_data[1]

	min_height_variate = min_height / dex_height
	max_height_variate = max_height / dex_height

	min_weight = weight-0.005
	max_weight = weight+0.005
	dex_weight = get_dex_weight(mon)

	min_final_weight_variate = min_weight / dex_weight
	max_final_weight_variate = max_weight / dex_weight

	if min_height_variate < classes[4]: #everything except XXL
		#formula for classes 1-4 is as follows:
		#final_weight_variate = weight_variate + (height_variate^2 - 1)
		#final_weight_variate is a relatively well-known value
		#so the minimum possible weight variate occurs when the height variate is as BIG as possible
		#and therefore the weight variate has to be lower to balance it out to the final value
		min_weight_variate = min_final_weight_variate - (max_height_variate**2 - 1)
		#and the other way around for the max weight variate
		max_weight_variate = max_final_weight_variate - (min_height_variate**2 - 1)
	else: #XXL mons
		#formula for class 5 is as follows:
		#final_weight_variate = weight_variate + (height_variate - 1)
		min_weight_variate = min_final_weight_variate - (max_height_variate - 1)
		max_weight_variate = max_final_weight_variate - (min_height_variate - 1)
	#todo - clean up this logic so that something that could be in either class takes the min/max of each

	#print("Weight variate is between",min_weight_variate,"and",max_weight_variate)
	#print("Height variate is between",min_height_variate,"and",max_height_variate)

	return [[min_weight_variate, max_weight_variate], [min_height_variate, max_height_variate]]

def get_evolutions(template):
	settings = template['data']['pokemonSettings']
	if "evolutionBranch" not in settings:
		return []

	branches = settings['evolutionBranch']
	evolution_templates = []
	for branch in branches:
		if 'temporaryEvolution' in branch:
			continue
		elif 'form' in branch:
			evo_name = branch['form']
		else:
			evo_name = branch['evolution']
		evo_template = get_template(evo_name)
		evo_obj = {'name': evo_name, 'template': evo_template}
		evolution_templates.append(evo_obj)

	return evolution_templates

def check_evo_chances(mon, weight, height, override_class_size=False):
	mon = format_name(mon)
	variates = get_variates(mon, height, weight)

	#if mon name was incorrect, fail out
	if not variates:
		return None

	template = get_template(mon)

	#check class size
	classes = get_class_boundaries(mon)
	min_class_boundaries = classes[1][:5]
	max_class_boundaries = classes[1][1:]
	if override_class_size:
		overrides = ["XXS", "XS", "AVG", "XL", "XXL"]
		min_class_size = override_class_size - 1
		max_class_size = override_class_size - 1
		print("Overriding class size to",overrides[override_class_size - 1])
	else:
		if variates[1][0] < 0.50:
			min_class_size = 0
		elif variates[1][0] < 0.75:
			min_class_size = 1
		elif variates[1][0] < 1.25:
			min_class_size = 2
		elif variates[1][0] < 1.50:
			min_class_size = 3
		else:
			min_class_size = 4

		if variates[1][1] < 0.50:
			max_class_size = 0
		elif variates[1][1] < 0.75:
			max_class_size = 1
		elif variates[1][1] < 1.25:
			max_class_size = 2
		elif variates[1][1] < 1.50:
			max_class_size = 3
		else:
			max_class_size = 4

	if max_class_size != min_class_size:
		clrprint("Warning: class size unknown", clr="red")
		if max_class_size == 4:
			#if the class size isn't explicitly XXL, we don't handle XXL class size changes on evolution
			clrprint("ERROR: Evolutions of different XXL class will be incorrect", clr="red")

	#because the height variates reroll completely on evolve, the ones of the prevo are irrelevant
	#so we just over-write them
	#[UPDATE] as of ~11 April 2024, height variates no longer reroll on evolved
	#[		] and therefore we don't rewrite them here anymore
	#[		] (there's probably lots of optimisations to make to the code now this is unnecessary)
	#variates[1][0] = min_class_boundaries[min_class_size]
	#variates[1][1] = max_class_boundaries[max_class_size]

	evos = get_evolutions(template)
	count = 0
	if len(evos) > 0:
		while count < len(evos):
			evo = evos[count]['template']
			settings = evo['data']['pokemonSettings']

			#get the class boundaries of the evolution
			#(this is a bit grossly inefficient)
			new_bounds = get_class_boundaries(evos[count]['name'])

			#evolutions may have different height class sizes than the pokemon their evolving from
			#so even though the height variate doesn't reroll, it may *adjust*
			#no evolution line exists with disparities for XXS,XS,Avg,XL classes, so we only need
			#to look at this for XXLs
			if min_class_size == 4:
				#the correct way to adjust any bound is to calculate its distance from lower bound
				#divide this by the total range of the bounds of that class size
				#then multiply it by the total range of the bounds of the new class size
				old_bound_range = classes[1][min_class_size+1] - classes[1][min_class_size]
				new_bound_range = new_bounds[1][min_class_size+1] - new_bounds[1][min_class_size]
				#and build the new variates
				adj_h_variates = [
					new_bounds[1][min_class_size]+(variates[1][0]-classes[1][min_class_size])/old_bound_range*new_bound_range,
					new_bounds[1][min_class_size]+(variates[1][1]-classes[1][min_class_size])/old_bound_range*new_bound_range
				]
			else:
				#if we're not adjusting the variates, just copy them over
				adj_h_variates = [variates[1][0], variates[1][1]]

			if override_class_size:
				#we have two values: the class boundary, and the +- 0.005m value from the storage
				#the true value must remain within both of these values
				#so for the lower bound, we take the max(), and for the higher bound, the min()
				adj_h_variates[0] = max(new_bounds[1][:5][min_class_size], adj_h_variates[0])
				adj_h_variates[1] = min(new_bounds[1][1:][max_class_size], adj_h_variates[1])

			#calculate combined variates now that we've (potentially) adjusted the height variates
			if min_class_size == 4:
				#guaranteed XXLs have a different weight formula
				combined_variates = [(variates[0][0] + (adj_h_variates[0] - 1)), (variates[0][1] + (adj_h_variates[1] - 1))]
			else:
				combined_variates = [(variates[0][0] + (adj_h_variates[0]**2 - 1)), (variates[0][1] + (adj_h_variates[1]**2 - 1))]

			#for mons with split genders (e.g., Pyroar) this DOES print both
			#but doesn't indicate which is which. Should probably fix at some point
			print("Calculating sizes for",settings['pokemonId'])

			#calculate min/max heights
			min_height = settings['pokedexHeightM'] * adj_h_variates[0]
			max_height = settings['pokedexHeightM'] * adj_h_variates[1]
			#now for the weights
			min_weight = settings['pokedexWeightKg'] * combined_variates[0]
			max_weight = settings['pokedexWeightKg'] * combined_variates[1]
			#declare vars for records
			short = None
			tall = None
			light = None
			heavy = None
			#and check what records to print
			print_small = False
			print_large = False
			print_evo = None

			if 'scores' in template:
				#need to check both in case an evo exists that doesn't have a chart
				if 'scores' in evo:
					print_small = adj_h_variates[0] < 1
					print_large = adj_h_variates[1] > 1
					short = evo['scores']['Pokédex Shortest']
					tall = evo['scores']['Pokédex Tallest']
					light = evo['scores']['Pokédex Lightest']
					heavy = evo['scores']['Pokédex Heaviest']
					print_evo = False #unless we trigger a possible higher score, don't evolve
				else:
					clrprint("Chart missing for " + settings['pokemonId'], clr="red")

			#start printing output
			print("Height between",'{0:.2f}m'.format(min_height),"and",'{0:.2f}m'.format(max_height))
			if print_small:
				print("Record shortest: {0}m".format(short))
				if short > min_height:
					print_evo = True
			if print_large:
				print("Record tallest: {0}m".format(tall))
				if tall < max_height:
					print_evo = True
			print("Weight between",'{0:.2f}kg'.format(min_weight),"and",'{0:.2f}kg'.format(max_weight))
			if print_small:
				print("Record lightest: {0}kg".format(light))
				if light > min_weight:
					print_evo = True
			if print_large:
				print("Record heaviest: {0}kg".format(heavy))
				if heavy < max_weight:
					print_evo = True
			#check if we should evolve this mon
			if print_evo:
				clrprint("EVOLVE. This can set a new high score.", clr="green")
			else:
				clrprint("DO NOT EVOLVE. No new record can be set.", clr="black")

			#and handle any third-stage evos
			evos = evos + get_evolutions(evo)
			count += 1
	else:
		print("No evos found. Possible weight multipliers are in this range:")
		combined_variates = [(variates[0][0] + (variates[1][0]**2 - 1)), (variates[0][1] + (variates[1][1]**2 - 1))]
		print(combined_variates)

def analyse_score(score):
	#get Pokemon from the chart name
	#todo - need to handle form names specially here
	mon = format_name(score['chart'][8:])

	#don't analyse Pumpkaboo line as we don't know how it works yet
	if "PUMPKABOO" in mon or "GOURGEIST" in mon:
		print("Skipping analysis of",mon)
		return False

	#don't analyse Zorua highest weights, because they're bugged in-game
	if "ZORUA" in mon or "ZOROARK" in mon:
		if score['polarity'] == 1 and score['size_type'] == 0:
			print("Skipping analysis of heaviest",mon)
			return False

	print("Analysing mon: ",mon)

	size_set = score['score']
	#we need to offset the scores by the rounding margin used to calculate win chances
	#in order to get the chance of *setting* that score, rather than the chances of *beating* it
	#score['polarity'] is 0 for low, 1 for high
	if score['polarity'] == 0:
		size_beaten = score['score'] + 0.01
	elif score['polarity'] == 1:
		size_beaten = score['score'] - 0.01
	else:
		clrprint("ERROR: polarity", score['polarity'], "is not valid", clr="red")
		return

	#score['size_type'] is 0 for weight, 1 for height
	#note that get_*eight_chance returns a list of two variables
	#idx 0 is -1 if lower is better, +1 if higher is better. We can ignore that.
	#idx 1 is the list of win chances depending on species class. This is what we want
	if score['size_type'] == 0:
		chance_to_set = get_weight_chance(mon, size_beaten)[1]
		chance_to_beat = get_weight_chance(mon, size_set)[1]
	elif score['size_type'] == 1:
		chance_to_set = get_height_chance(mon, size_beaten)[1]
		chance_to_beat = get_height_chance(mon, size_set)[1]
	else:
		clrprint("ERROR: score size size_type", score['size_type'], "is not valid", clr="red")
		return
	print(chance_to_set)

	#construct string
	if chance_to_beat == 0: #report all perfect scores
		output = "**New perfect score!**\n"
	elif chance_to_set <= 0.001: #report all 1 in >1k scores
		output = "**New rare score!**\n"
	else: #don't report anything else
		return None

	#if we get here an output is desired

	#then start building the string
	output += score['flag_emoji'] + " " + score['user_link'] + " just scored " + score['score_link']
	output += " (Pos: **" + score['pos'] + "**" + score['medal'] + ")\n"
	output += score['game'] + " → " + score['chart_link'] + "\n"
	#first, generate the numbers indicating rarity
	#we check that this is >0 first to avoid reporting incorrect data for XXS heights (see below)
	if chance_to_set > 0:
		fraction = round(1/chance_to_set)
		size = max(3,round(math.log(fraction,10))-1) #this will show e.g., 5 decimals for a 1 in 1mil chance
		percentage = str(round(chance_to_set * 100,size))
		output += "This score was a " +percentage+"% chance of occurring (1 in "+str(fraction)+")"
	else:
		output += "This score appears to be impossible. If it's definitely correct, yell at <@101709643822157824> to fix his code."

	return output

def getHeightRange(mon):
	template = get_template(mon)
	min_xxs = template['sizeclasses'][0]
	min_xs = template['sizeclasses'][1]
	max_xxl = template['sizeclasses'][5]
	min_xxs_round = math.floor(min_xxs*100)/100.0
	min_floor_bug = math.floor((min_xs-0.01)*100)/100.0
	#check to see if we can dip under the minimum because of the floor weirdness
	score_min = min(min_xxs_round, min_floor_bug)
	#build results
	true_range = [min_xxs, max_xxl]
	score_range = [score_min, round(max_xxl*100)/100.0]
	return [true_range, score_range]

#scraper for chart-by-chart
def load_all_charts():
	url = "https://cyberscore.me.uk/games/2006.json"
	page = requests.get(url) #TODO - import cookies here in a safe way
	pogo = json.loads(page.content)

	chart_groups = pogo['chart_groups']
	iter_groups = []
	#removed Pokedex Lightest and Heaviest for a bit after having already iterated over it and fixed a bug with Heaviest
	target_groups = ["Pokédex Lightest", "Pokédex Heaviest", "Pokédex Shortest", "Pokédex Tallest"]

	for group in chart_groups:
		if group['group_name'] in target_groups:
			iter_groups.append(group)

	#slightly redundant way of doing things, consolidate these loops if we don't need the data repeatedly

	#skip lightest/heaviest until later
	for group in iter_groups:
		gname = group['group_name']
		for chart in group['charts']: #Shortest
			cname = chart['chart_name']
			chart_json = download_chart(chart)

			analyse_chart(chart_json, gname, cname)

def load_charts_from_disk():
	global processed_charts
	path = "data/chart_jsons/"
	l = listdir(path)
	files = [f for f in l if isfile(join(path, f))]
	print("Loading",len(files),"charts")
	i = 0
	for file in files:
		i+=1
		chart = load_chart_from_disk(join(path,file))
		chart_name = chart['chart_name']
		template_name = get_template_name(format_name(chart_name[8:]))
		chart_group = chart['group_name']
		#match group
		if "Lightest" in chart_group:
			processed_charts["Lightest"][template_name] = chart
		elif "Heaviest" in chart_group:
			processed_charts["Heaviest"][template_name] = chart
		elif "Shortest" in chart_group:
			processed_charts["Shortest"][template_name] = chart
		elif "Tallest" in chart_group:
			processed_charts["Tallest"][template_name] = chart
		if i%1000 == 0:
			print("Loaded",i,"charts")
	print("Loaded all charts")

def load_chart_from_disk(path):
	f = open(path, "r")
	chart_json = json.load(f)
	return chart_json

def get_leader(size_type, name):
	chart = get_chart(size_type, name)
	cname = chart['group_name'] + " – " + chart['chart_name']
	score = chart['scoreboard'][0]
	suffix_type = "kg" if (size_type == "Heaviest" or size_type == "Lightest") else "m"
	print(score['username'], "is the leader on", cname, "with a score of", score['submission'], suffix_type)

def get_xx_leaderboard(size_type, mode="print"):
	r = {}
	chart_count = len(processed_charts[size_type])
	for cname in processed_charts[size_type]:
		chart = processed_charts[size_type][cname]

		template = get_template(cname)

		#manual handling for edge cases
		if "PUMPKABOO" in cname:
			if size_type == "Shortest" or "PUMPKABOO_SUPER" not in cname:
				#for Tallest SUPER we can just use the existing XXL bound
				#but for everything else we have to skip, as no XXS or XXL exists
				chart_count -= 1
				continue

		scoreboard = chart['scoreboard']
		for sub in scoreboard:
			if sub['username'] not in r: #init any users seen for the first time
				r[sub['username']] = 0
			if size_type == "Tallest" and sub['submission'] >= template['sizeclasses'][4]:
				r[sub['username']] += 1
			elif size_type == "Shortest" and sub['submission'] < template['sizeclasses'][1]:
				r[sub['username']] += 1

	output = ""
	last_score = 0
	curr_pos = 0
	last_pos = 0
	for user in sorted(r, key=r.get, reverse=True):
		curr_pos += 1
		#print position
		output += "#"
		if r[user] == last_score:
			output += str(last_pos)
		else:
			output += str(curr_pos)
			last_pos = curr_pos
		#print username
		output += " " + user
		#print score (and update tiechecker)
		output += " " + str(r[user]) + "\n"
		last_score = r[user]
	if mode == "print":
		print(output)
	else:
		return [r, chart_count]

def get_xxl_leaderboard(mode = "print"):
	return get_xx_leaderboard("Tallest", mode)

def get_xxs_leaderboard(mode = "print"):
	return get_xx_leaderboard("Shortest", mode)

def get_xxl_count(username):
	leaderboard, chart_count = get_xxl_leaderboard("return")
	xxl_count = leaderboard[username]
	comp_pct = 100/chart_count*xxl_count
	print("Completion rate:", str(xxl_count)+"/"+str(chart_count), "("+"{:.2f}".format(comp_pct)+"%)")

def get_user_score(scoreboard, user):
	score = None
	for sub in scoreboard:
		if sub['username'] == user:
			score = sub
			break
	return score

def get_chart(size_type, name):
	name = get_template_name(format_name(name))
	return processed_charts[size_type][name]

def download_chart(chart_data):
	page = requests.get(chart_data['chart_url']['json'])
	chart = json.loads(page.content)
	#todo – change this path when set up properly
	local_path = "data/chart_jsons/" + str(chart_data['chart_id']) + ".json"
	with open(local_path, "w+") as f:
		json.dump(chart, f)
	return chart

def analyse_chart(chart_json, gname, cname):
	if len(chart_json['scoreboard']) == 0:
		print("No scores submitted for", cname)

	mon = format_name(cname[8:])
	weight_range = []
	height_range = []

	if "Lightest" in gname or "Heaviest" in gname:
		weight_range = [0, get_dex_weight(mon)*2.75]
	elif "Shortest" in gname or "Tallest" in gname:
		#don't analyse Pumpkaboo line as we don't know how it works yet
		if "PUMPKABOO" in mon or "GOURGEIST" in mon:
			print("Skipping height analysis of",mon)
			return

		height_range = getHeightRange(mon)[1] #[1] takes only the score-rounded height range
		if not height_range:
			print("Error generating height_range for",cname)
			return
	else:
		print("ERROR: group name", gname, "not valid")
		return

	for sub in chart_json['scoreboard']:
		rid = sub['record_id']
		pos = sub['chart_pos'] #accounts for ties, e.g., a two-way tie for 1st will both show 1st
		user = sub['username']
		uid = sub['user_id']
		score = sub['submission']
		best_score = None
		invalid_score = False

		if "Lightest" in gname:
			best_score = weight_range[0]
			invalid_score = score < best_score
		elif "Heaviest" in gname:
			best_score = weight_range[1]
			invalid_score = score > best_score
		elif "Shortest" in gname:
			best_score = height_range[0]
			invalid_score = score < best_score
		elif "Tallest" in gname:
			best_score = height_range[1]
			invalid_score = score > best_score

		if invalid_score: #[1] for Tallest
			print("Invalid score on",gname,"–",cname,"by",user)
			print("Top score of",score,"but best possible score is",best_score)

def load_personal_records(sessid):
	url = "https://cyberscore.me.uk/games/2006.json"
	page = requests.get(url, cookies={'PHPSESSID':sessid})
	data = json.loads(page.content)
	chart_groups = data['chart_groups']
	for group in chart_groups:
		target_groups = ["Pokédex Lightest", "Pokédex Heaviest", "Pokédex Shortest", "Pokédex Tallest"]
		gname = group['group_name']
		if group['group_name'] not in target_groups:
			continue
		#if we get here, it's a size group, and we want to save scores
		for chart in group['charts']:
			#find the exact template ready to add
			cname = chart['chart_name']
			template = get_template(format_name(cname[8:]))
			if 'scores' not in template:
				template['scores'] = {}

			if chart['record']['submission'] is None:
				#this is an unsubmitted score
				template['scores'][gname] = None
			else:
				template['scores'][gname] = chart['record']['submission']

#this function doesn't *do* anything, and isn't used by the rest of the module
#but is useful to manually run occasionally to check if Niantic have broken any gm data
#current expected output:
#Scatterbug line XXS is 0.25x not 0.49x
#H-Avalugg bounds use Avalugg's (this is hardcoded to correctly predict sizes)
#Beartic doesn't have bounds (this won't print, as this program fixes it in template generation)
#Pumpkaboo line is fucked
#Size data not available for Cursola (likely just not implemented yet)
def sanity_check_class_boundaries():
	for mon in pokemon_templates:
		template = pokemon_templates[mon]
		if "sizeclasses" not in template:
			print("Size data not available for",mon)
			continue

		#only print one of each Scatterbug (they're all identical)
		if "SCATTERBUG" in mon or "SPEWPA" in mon or "VIVILLON" in mon:
			if "ARCHIPELAGO" not in mon:
				continue
		#Pumpkaboo line still uses old system
		if "PUMPKABOO" in mon or "GOURGEIST" in mon:
			if mon == "V0710_POKEMON_PUMPKABOO_AVERAGE":
				print("Pumpkaboo is incompatible with the modern XXS/XXL system.")
			continue

		classes = template['sizeclasses']
		height = template['data']['pokemonSettings']['pokedexHeightM']
		name = template['templateId']
		if classes[0] != round(0.49 * height,5):
			print("XXS lower bound for",name,"does not match")
			print("Expected 0.49, got",round(classes[0]/height,5))
		if classes[1] != round(0.50 * height,5):
			print("XS lower bound for",name,"does not match")
			print("Expected 0.50, got",round(classes[1]/height,5))
		if classes[2] != round(0.75 * height,5):
			print("XS upper bound for",name,"does not match")
			print("Expected 0.75, got",round(classes[2]/height,5))
		if classes[3] != round(1.25 * height,5):
			print("XL lower bound for",name,"does not match")
			print("Expected 1.25, got",round(classes[3]/height,5))
		if classes[4] != round(1.50 * height,5):
			print("XXL lower bound for",name,"does not match")
			print("Expected 1.50, got",round(classes[4]/height,5))
		if classes[5] != round(1.55 * height,5) and classes[5] != round(1.75 * height,5) and classes[5] != round(2 * height,5):
			print("XXL upper bound for",name,"does not match")
			print("Expected 1.55/1.75/2.00, got",round(classes[5]/height,5))
