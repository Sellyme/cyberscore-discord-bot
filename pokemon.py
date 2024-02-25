import requests, re, json, csv, math
import cmfn, config
from pokemon_cdfs.xxl_classes_dict import xxl_sizes #dictionary mapping pokemon_templates keys to XXL-1, XXL-2, or XXL-3
from clrprint import clrprint

pokemon_templates = {}
pokemon_forms_by_id = {}
pokemon_forms_by_name = {}
pokemon_class_boundaries = {}

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

#takes in a height from the game master and calculates the variate for that mon, rounding off fp errors
def rounded_variate(height, dex_height):
	return round(height/dex_height,5)

#returns an array of [dex_height, [class1, class2, class3, etc]]
#where class1...6 represent the (overlapping) lower and upper boundaries of each class 
def get_class_boundaries(mon):
	mon = get_template_name(mon)
	height = get_dex_height(mon)
	#H-Avalugg is still VERY broken and doesn't have any actual data available
	#right now the K-Avalugg data is being inserted into its template during gm loading
	#so to make that workable, for the calculations we'll hardcode K-Avalugg's dex height
	#and assume that H-Avalugg actually has all the same class boundaries
	#this could be incorrect, but it's at least less incorrect than calculating them with the wrong heights
	if "AVALUGG" in mon.upper() and "HISUI" in mon.upper():
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
		if "AVALUGG" in mon.upper() and "HISUI" in mon.upper():
			height = real_height
		#and return output
		return [height, [xxs_low, xs_low, xs_high, xl_low, xxl_low, xxl_high]]
	else:
		return False

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
	#replace all spaces with underscores: "tapu koko" → "TAPU_KOKO"; "JANGMO-O" → "JANGMOO"
	name = name.upper().replace(" ","_").replace("-","_").replace("é","e").replace("É","E").replace("♀","F").replace("♂","M")
	for char in ":'’.": #strip special chars: "FARFETCH'D" → "FARFETCHD"; "MR._MIME" → "MR_MIME"
		if char in name:
			name = name.replace(char, "")
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
	
	#handle Rotom, which is stored in GM as ROTOM_TYPE but in dex as "Type Rotom"
	if "ROTOM" in mon:
		mon_chunks = mon.split("_")
		if mon_chunks[0] == "ROTOM":
			return mon
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
	else:
		print("Couldn't find template for",mon)
		return False

def get_template(mon): #mon is always a name of format DARUMAKA_GALAR
	template_name = get_template_name(mon)
	if template_name in pokemon_templates:
		return pokemon_templates[template_name]
	else:
		return False

def get_variates(mon, height, weight):
	mon = get_template_name(mon)

	#if mon name was incorrect, fail out
	if not mon:
		return False

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
		evolution_templates.append(evo_template)
	
	return evolution_templates

def check_evo_chances(mon, weight, height, override_class_size=False):
	#todo - implement override_class_size when this is unknowable from the height
	mon = format_name(mon)
	variates = get_variates(mon, height, weight)

	#if mon name was incorrect, fail out
	if not variates:
		return False

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
	
	#because the height variates reroll completely on evolve, the ones of the prevo are irrelevant
	#so we just over-write them
	variates[1][0] = min_class_boundaries[min_class_size]
	variates[1][1] = max_class_boundaries[max_class_size]

	#combine both height and weight variates into one number for final weight
	combined_variates = [(variates[0][0] + (variates[1][0]**2 - 1)), (variates[0][1] + (variates[1][1]**2 - 1))]

	evos = get_evolutions(template)
	count = 0
	if len(evos) > 0:
		while count < len(evos):
			evo = evos[count]
			settings = evo['data']['pokemonSettings']
			
			#for mons with split genders (e.g., Pyroar) this DOES print both
			#but doesn't indicate which is which. Should probably fix at some point
			print("Calculating sizes for",settings['pokemonId'])
			
			#calculate min/max heights
			min_height = settings['pokedexHeightM'] * variates[1][0]
			max_height = settings['pokedexHeightM'] * variates[1][1]
			#now for the weights
			min_weight = settings['pokedexWeightKg'] * combined_variates[0]
			max_weight = settings['pokedexWeightKg'] * combined_variates[1]
			#and check what records to print
			print_small = False
			print_large = False
			print_evo = None

			if 'scores' in template:
				#need to check both in case an evo exists that doesn't have a chart
				if 'scores' in evo:
					print_small = variates[1][0] < 1
					print_large = variates[1][1] > 1
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
			if print_evo == False:
				clrprint("DO NOT EVOLVE. No new record can be set.", clr="black")
			elif print_evo == True:
				clrprint("EVOLVE. This can set a new high score.", clr="green")
			
			#and handle any third-stage evos
			evos = evos + get_evolutions(evo)
			count += 1
	else:
		print("No evos found. Possible weight multipliers are in this range:")
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
		if score['polarity'] == 1 and score['type'] == 0:
			print("Skipping analysis of heaviest",mon)
			return False
	
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
		frac = round(1/chance_to_set)
		size = max(3,round(math.log(frac,10))-1) #this will show e.g., 5 decimals for a 1 in 1mil chance
		perc = str(round(chance_to_set * 100,size))
		output += "This score was a " +perc+"% chance of occurring (1 in "+str(frac)+")"
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
			chart_json = get_chart(chart)
			
			analyse_chart(chart_json)

def get_chart(chart_data):
	page = requests.get(chart_data['chart_url']['json'])
	chart = json.loads(page.content)
	#todo – change this path when set up properly
	local_path = "C:/Programming/Python/CS/Discord bot/chart_jsons/" + str(chart_data['chart_id']) + ".json"
	f=open(local_path, "w+")
	json.dump(chart, f)
	return chart

def analyse_chart(chart_json):
	if len(chart_json['scoreboard']) == 0:
		print("No scores submitted for", cname)
	
	mon = format_name(cname[8:])

	if "Lightest" in gname or "Heaviest" in gname:
		wrange = [0, get_dex_weight(mon)*2.75]
	elif "Shortest" in gname or "Tallest" in gname:
		#don't analyse Pumpkaboo line as we don't know how it works yet
		if "PUMPKABOO" in mon or "GOURGEIST" in mon:
			print("Skipping height analysis of",mon)
		
		hrange = getHeightRange(mon)[1] #[1] takes only the score-rounded height range
		if not hrange:
			print("Error generating hrange for",cname)
			return

	for sub in chart_json['scoreboard']:
		rid = sub['record_id']
		pos = sub['chart_pos'] #accounts for ties, e.g., a two-way tie for 1st will both show 1st
		user = sub['username']
		uid = sub['user_id']
		score = sub['submission']

		if "Lightest" in gname:
			best_score = wrange[0]
			invalid_score = score < best_score
		elif "Heaviest" in gname:
			best_score = wrange[1]
			invalid_score = score > best_score
		elif "Shortest" in gname:
			best_score = hrange[0]
			invalid_score = score < best_score
		elif "Tallest" in gname:
			best_score = hrange[1]
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
		#if we get here, it's a size group and we want to save scores
		for chart in group['charts']:
			#find the exact template ready to add
			cname = chart['chart_name']
			template = get_template(format_name(cname[8:]))
			if 'scores' not in template:
				template['scores'] = {}
		
			if chart['record']['submission'] == None:
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