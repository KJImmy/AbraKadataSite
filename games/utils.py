import requests
import datetime as dt
import json
import math

from django.db.models import Count,Q
from .models import Game,GamePlayerRelation,PokemonUsage,MoveUsage,Player
from .parser import parse_game
from tiers.models import Tier
from pokemon.models import Pokemon,Type,Move,Ability,Item,Move
from users.models import PokemonOnTeam,MoveOfPokemonOnTeam,UserTeam
from games.models import Player

nature_dict = {"Lonely":{"Atk":"+","Def":"-"},
				"Brave":{"Atk":"+","Spe":"-"},
				"Adamant":{"Atk":"+","SpA":"-"},
				"Naughty":{"Atk":"+","SpD":"-"},
				"Bold":{"Def":"+","Atk":"-"},
				"Relaxed":{"Def":"+","Spe":"-"},
				"Impish":{"Def":"+","SpA":"-"},
				"Lax":{"Def":"+","SpD":"-"},
				"Timid":{"Spe":"+","Atk":"-"},
				"Hasty":{"Spe":"+","Def":"-"},
				"Jolly":{"Spe":"+","SpA":"-"},
				"Naive":{"Spe":"+","SpD":"-"},
				"Modest":{"SpA":"+","Atk":"-"},
				"Mild":{"SpA":"+","Def":"-"},
				"Quiet":{"SpA":"+","Spe":"-"},
				"Rash":{"SpA":"+","SpD":"-"},
				"Calm":{"SpD":"+","Atk":"-"},
				"Gentle":{"SpD":"+","Def":"-"},
				"Sassy":{"SpD":"+","Spe":"-"},
				"Careful":{"SpD":"+","SpA":"-"},
				"Hardy":{},
				"Docile":{},
				"Serious":{},
				"Bashful":{},
				"Quirky":{}}

class ActiveMon:
	def __init__(self):
		self.species = None
		self.ability = None
		self.item = None
		self.level = None
		self.nature = None
		self.stats = {"HP":None,"Atk":None,"Def":None,"SpA":None,"SpD":None,"Spe":None}
		self.EVs = {"HP":None,"Atk":None,"Def":None,"SpA":None,"SpD":None,"Spe":None}
		self.IVs = {"HP":31,"Atk":31,"Def":31,"SpA":31,"SpD":31,"Spe":31}
		self.base_stats = {"HP":None,"Atk":None,"Def":None,"SpA":None,"SpD":None,"Spe":None}
		self.move_list = []
		self.tera_type = None

	def __eq__(self,other):
		if self.__class__ != other.__class__:
			return False
		return self.__dict__ == other.__dict__

	def get_base_stats(self):
		# Get Pokemon Objcet
		this_pokemon = Pokemon.objects.get(pokemon_unique_name=self.species)
		self.base_stats["HP"] = this_pokemon.stats_hp
		self.base_stats["Atk"] = this_pokemon.stats_attack
		self.base_stats["Def"] = this_pokemon.stats_defense
		self.base_stats["SpA"] = this_pokemon.stats_special_attack
		self.base_stats["SpD"] = this_pokemon.stats_special_defense
		self.base_stats["Spe"] = this_pokemon.stats_speed

def normalize_name(name):
	if name == "Flabébé":
		name = "flabebe"
	elif "Flabébé" in name:
		name = "flabebe"
	elif name == "Floette-Blue":
		name = "floette"
	elif name == "Floette-White":
		name = "floette"
	elif name == "Floette-Yellow":
		name = "floette"
	elif name == "Flabébé-Blue":
		name = "flabebe"
	elif name == "Tauros-Paldea-Aqua":
		name = "Tauros-Paldea-Water"
	elif name == "Tauros-Paldea-Blaze":
		name = "Tauros-Paldea-Fire"
	elif name == "Tauros-Paldea-Combat":
		name = "Tauros-Paldea"
	name = name.lower()
	name = name.replace(" ","-")
	name = name.replace("'","")
	name = name.replace("’","")
	name = name.replace(".","")
	name = name.replace("%","")
	name = name.replace(":","")
	return name

def adjust_stats_for_items_and_abilities(mon):
	item_list = [
		#Conditional Items
		"deep-sea-scale",
		"deep-sea-tooth",
		"eviolite",
		"light-ball",
		"metal-powder",
		"quick-powder",
		"soul-dew", #THIS ONE DEPENDS ON THE GEN
		"thick-club",
		#Non-Conditional Items
		"choice-band",
		"choice-specs",
		"choice-scarf",
		"assault-vest",
		"power-weight",
		"power-bracer",
		"power-anklet",
		"power-band",
		"power-lens",
		"power-belt",
		"iron-ball"
	]
	ability_list = [
		"gorrilla-tactics"
	]
	if mon.item not in item_list:
		return mon
	elif mon.item == "choice-band":
		mon.stats["Atk"] = math.ceil(mon.stats["Atk"]/1.5)
	elif mon.item == "choice-specs":
		mon.stats["SpA"] = math.ceil(mon.stats["SpA"]/1.5)
	elif mon.item == "choice-scarf":
		mon.stats["Spe"] = math.ceil(mon.stats["Spe"]/1.5)
	return mon

def validate_spread(mon):
	valid = True
	EV_total = 0
	
	for stat in mon.stats.keys():
		EV_total+=mon.EVs[stat]
		if mon.EVs[stat] > 252 or mon.EVs[stat] < 0 or mon.IVs[stat] < 0 or mon.IVs[stat] > 31:
			valid = False

	if EV_total > 510:
		valid = False

	return valid

def find_nature(invalid_stats,mon):
	possible_natures = []

	if len(invalid_stats) == 2:
		for stat in invalid_stats:
			if mon.EVs[stat] < 0:
				neg_stat = stat
			elif mon.EVs[stat] > 252:
				pos_stat = stat

		stat_changes = {pos_stat:"+",neg_stat:"-"}

		for nature in nature_dict.keys():
			if nature_dict[nature] == stat_changes:
				# print(nature)
				possible_natures.append(nature)

	elif len(invalid_stats) == 1:
		stat = invalid_stats[0]
		if mon.EVs[stat] < 0:
			for nature in nature_dict:
				if stat in nature_dict[nature].keys():
					if nature_dict[nature][stat] == "-":
						possible_natures.append(nature)
		elif mon.EVs[stat] > 252:
			for nature in nature_dict:
				if stat in nature_dict[nature].keys():
					if nature_dict[nature][stat] == "+":
						possible_natures.append(nature)

	else:
		boosted_stats = []
		possible_natures = []
		for stat in mon.EVs.keys():
			if stat != "HP" and mon.EVs[stat] > 0:
				boosted_stats.append(stat)
		for stat in boosted_stats:
			for nature in nature_dict:
				if stat in nature_dict[nature].keys():
					if nature_dict[nature][stat] == "+":
						possible_natures.append(nature)

	return possible_natures

def get_nature_mod(nature,stat):
	nature_mod = 1
	if nature != None:
		if stat in nature_dict[nature].keys():
			if nature_dict[nature][stat] == "+":
				nature_mod = 1.1
			elif nature_dict[nature][stat] == "-":
				nature_mod = 0.9

	return nature_mod

def calc_stat(stat,mon):
	if stat == "HP":
		calc = math.floor(((2*mon.base_stats[stat]+mon.IVs[stat]+math.floor(mon.EVs[stat]/4))*mon.level)/100)+mon.level+10
	else:
		nature_mod = get_nature_mod(mon.nature,stat)
		calc = math.floor((math.floor((2*mon.base_stats[stat]+mon.IVs[stat]+math.floor(mon.EVs[stat]/4))*mon.level/100)+5)*nature_mod)
	return calc

def reverse_calc_spread(mon):
	valid = {"total":True}
	# Assume 31 IVs in every stat and neutral nature
	for stat in mon.IVs.keys():
		mon.IVs[stat] = 31

	# Reverse Calc stats with 31IV assumption
	for stat in mon.stats.keys():
		# print("\n"+stat)
		if stat == "HP":
			mon.EVs[stat] = mon.stats[stat] - 10 - mon.level
			mon.EVs[stat] *= 100/mon.level
			mon.EVs[stat] += -2*mon.base_stats[stat]-mon.IVs[stat]
			mon.EVs[stat] *= 4
			mon.EVs[stat] = round(mon.EVs[stat])

		else:
			nature_mod = get_nature_mod(mon.nature,stat)
			mon.EVs[stat] = mon.stats[stat]/nature_mod - 5
			mon.EVs[stat] *= 100/mon.level
			mon.EVs[stat] += -2*mon.base_stats[stat]-mon.IVs[stat]
			mon.EVs[stat] *= 4
			mon.EVs[stat] = round(mon.EVs[stat])
			# print(mon.EVs[stat])

		if mon.EVs[stat] < 0:
			mon.EVs[stat] = 0

		stat_from_temp = calc_stat(stat,mon)

		while stat_from_temp != mon.stats[stat]:
			# if stat == "Spe":
				# print(mon.EVs[stat],stat_from_temp,mon.stats[stat])
			if stat_from_temp < mon.stats[stat]:
				mon.EVs[stat] += 1
				stat_from_temp = calc_stat(stat,mon)
			elif stat_from_temp > mon.stats[stat]:
				mon.EVs[stat] += -1
				stat_from_temp = calc_stat(stat,mon)

	EV_total = 0
	invalid_stats = []

	for stat in mon.stats.keys():
		if mon.EVs[stat] < 0:
			invalid_stats.append(stat)
			continue
		elif mon.EVs[stat] > 252:
			invalid_stats.append(stat)
		EV_total+=mon.EVs[stat]

	for stat in invalid_stats:
		if mon.EVs[stat] < 0:
			hold_EV = mon.EVs[stat]
			mon.EVs[stat] = 0
			mon.IVs[stat] = 0
			stat_from_temp = calc_stat(stat,mon)

			if stat_from_temp < mon.stats[stat]:
				while stat_from_temp != mon.stats[stat] and mon.IVs[stat] >= 0 and mon.IVs[stat] <= 31:
					mon.IVs[stat] += 1
					stat_from_temp = calc_stat(stat,mon)

			if stat_from_temp != mon.stats[stat]:
				mon.EVs[stat] = hold_EV
			else:
				invalid_stats.remove(stat)

	if (len(invalid_stats) > 0 or EV_total > 510) and mon.nature == None:
		possible_natures = find_nature(invalid_stats,mon)
		# print(possible_natures)
		for nature in possible_natures:
			# print(nature)
			mon.nature = nature
			result = reverse_calc_spread(mon)
			if result[1]:
				# print(result[1])
				mon = result[0]
				break

	valid = validate_spread(mon)

	return mon,valid

def get_game_from_link(game):
	if game[-4:] != ".log":
		game+=".log"

	log = requests.get(game).text

	return log

def add_team_details(link,details_json,username):
	game = Game.objects.get(link=link)
	player = GamePlayerRelation.objects.get(game__link=link,player__username=username)

	# team_details = json.load(details_json)
	team_details=details_json

	# Construct each of the pokemon based on team details
	activemon_objects = []
	mon_name_list = []
	team_intersection = None
	for mon in team_details.keys():
		new_activemon = ActiveMon()
		mon_name_list.append(mon)
		# THIS NEEDS TO BE CHANGED TO USE THE .exists() METHOD, FILTER WITH ALL AVAILABLE ATTRIBUTES, ENSURE NULL VALUES WILL NOT
		# MESS UP THE SEARCH, BUT IT ALSO NEEDS TO CHECK THAT ALL INSTANCES ARE ON THE SAME TEAM
		# Can do this by getting a list of teams that have the pokemon. Once I have all pokemon get the intersection of all lists.
		# Also make sure the username is in the list of usernames associated with the user.
		# Check user associated with current username, if no associated users assign team to just the username
		pokemon_object = Pokemon.objects.get(pokemon_unique_name=normalize_name(mon))
		new_activemon.species = normalize_name(mon)

		# Get ability object and assign
		ability_object = Ability.objects.get(ability_unique_name=normalize_name(team_details[mon]['Ability']))
		new_activemon.ability = team_details[mon]['Ability']

		# Get item object and assign
		item_name = normalize_name(team_details[mon]['Item'])
		new_activemon.item = item_name
		
		# Get and assign stats
		new_activemon.level = team_details[mon]['Level']

		new_activemon.stats['HP'] = team_details[mon]['HP']
		new_activemon.stats['Atk'] = team_details[mon]['Atk']
		new_activemon.stats['Def'] = team_details[mon]['Def']
		new_activemon.stats['SpA'] = team_details[mon]['SpA']
		new_activemon.stats['SpD'] = team_details[mon]['SpD']
		new_activemon.stats['Spe'] = team_details[mon]['Spe']

		new_activemon.get_base_stats()
		new_activemon = adjust_stats_for_items_and_abilities(new_activemon)
		new_activemon = reverse_calc_spread(new_activemon)[0]

		if new_activemon.nature == None:
			new_activemon.nature = "Serious"

		# Assign tera type if available
		if team_details[mon]['Tera Type']:
			tera_type_object = Type.objects.get(type_name=normalize_name(team_details[mon]['Tera Type']))
			new_activemon.tera_type = normalize_name(team_details[mon]['Tera Type'])

		move_list = []
		for move in team_details[mon]['Move List']:
			move_list.append(normalize_name(move))

		new_activemon.move_list = move_list
		activemon_objects.append(new_activemon)

		# NEEDS TO FILTER FOR MOVE LIST AS WELL
		# get list of mons and teams with this build
		possible_teams_list = list(PokemonOnTeam.objects.filter(
			pokemon=pokemon_object,
			ability=ability_object,
			item=item_name,
			level=new_activemon.level,
			ev_hp=new_activemon.EVs['HP'],
			ev_atk=new_activemon.EVs['Atk'],
			ev_def=new_activemon.EVs['Def'],
			ev_spa=new_activemon.EVs['SpA'],
			ev_spd=new_activemon.EVs['SpD'],
			ev_spe=new_activemon.EVs['Spe'],
			iv_hp=new_activemon.IVs['HP'],
			iv_atk=new_activemon.IVs['Atk'],
			iv_def=new_activemon.IVs['Def'],
			iv_spa=new_activemon.IVs['SpA'],
			iv_spd=new_activemon.IVs['SpD'],
			iv_spe=new_activemon.IVs['Spe'],
			nature=new_activemon.nature,
			tera_type=tera_type_object).annotate(
			count=Count('move_of_user_pokemon',filter=Q(move_of_user_pokemon__move__move_unique_name__in=move_list))).filter(
			count=len(move_list)).values_list('team',flat=True))

		if not team_intersection:
			team_intersection = possible_teams_list
			continue

		team_intersection = list(set(team_intersection) & set(possible_teams_list))

	# IF THERE ARE NO EXISTING TEAMS, MAKE THE USER TEAM
	if team_intersection == []:
		cur_team = UserTeam()
		ps_username = Player.objects.get(username=username)
		cur_team.username = ps_username
		# IF username already connected to site account, then add account
		if ps_username.site_user:
			cur_team.site_user = ps_username.site_user

		cur_team.tier = game.tier
		cur_team.save()

		for mon in activemon_objects:
			new_mon_on_team = PokemonOnTeam()
			new_mon_on_team.pokemon = Pokemon.objects.get(pokemon_unique_name=mon.species)
			new_mon_on_team.team = cur_team

			new_mon_on_team.level = mon.level

			new_mon_on_team.ev_hp = mon.EVs['HP']
			new_mon_on_team.ev_atk = mon.EVs['Atk']
			new_mon_on_team.ev_def = mon.EVs['Def']
			new_mon_on_team.ev_spa = mon.EVs['SpA']
			new_mon_on_team.ev_spd = mon.EVs['SpD']
			new_mon_on_team.ev_spe = mon.EVs['Spe']

			new_mon_on_team.iv_hp = mon.IVs['HP']
			new_mon_on_team.iv_atk = mon.IVs['Atk']
			new_mon_on_team.iv_def = mon.IVs['Def']
			new_mon_on_team.iv_spa = mon.IVs['SpA']
			new_mon_on_team.iv_spd = mon.IVs['SpD']
			new_mon_on_team.iv_spe = mon.IVs['Spe']
			new_mon_on_team.nature = mon.nature

			ability_object = Ability.objects.get(ability_unique_name=normalize_name(mon.ability))
			new_mon_on_team.ability = ability_object
			new_mon_on_team.item = mon.item

			if mon.tera_type:
				type_object = Type.objects.get(type_name=normalize_name(mon.tera_type))
				new_mon_on_team.tera_type = type_object

			new_mon_on_team.save()

			for move in mon.move_list:
				move_object = Move.objects.get(move_unique_name=move)
				new_user_mon_move = MoveOfPokemonOnTeam()
				new_user_mon_move.pokemon = new_mon_on_team
				new_user_mon_move.move = move_object
				new_user_mon_move.save()

	elif len(team_intersection) == 1:
		cur_team = UserTeam.objects.get(pk=team_intersection[0])

	player.user_team = cur_team
	player.save()
	monusage = player.pokemon_of_player.all()
	for mon in monusage:
		user_mon = PokemonOnTeam.objects.get(team=cur_team,pokemon=mon.pokemon)
		mon.user_pokemon = user_mon
		mon.save()

	return team_intersection

		# IF team intersection is an empty list, team does not exist and should be constructed using activemon objects,
		# If 1 item in team intersection, assign to that team
		# If multiple items in team intersection... ? Might just pick first one, Otherwise I would need to prevent users from creating
		#	multiple identical teams

def add_game_from_link(link):
	game_check = Game.objects.filter(link=link).exists()
	if game_check:
		# Connect user to game submission, no need to upload game again
		print("Game already in db")
		return 0

	log = get_game_from_link(link)
	game_log = log.split('\n')
	game_obj = parse_game(game_log)

	if not game_obj.valid:
		print("Game is invalid")
		return 0

	# Add game

	# Get game format
	tier_check = Tier.objects.filter(generation=game_obj.generation,tier_name=game_obj.tier).exists()

	# Make format if missing
	if tier_check:
		tier = Tier.objects.get(generation=game_obj.generation,tier_name=game_obj.tier)
	else:
		# UPDATE MODEL TO ACCEPT UNCATEGORIZED STYLE FOR NEW FORMAT, also change valid default to False
		tier = Tier(generation=game_obj.generation,tier_name=game_obj.tier,tier_display_name=game_obj.tier,
							style='VGC',valid=False)
		tier.save()

	time = dt.datetime.fromtimestamp(game_obj.start_time)
	added_game = Game(start_time=time,link=link,tier=tier,
						public=False,ranked=game_obj.ranked)
	added_game.save()

	for p in game_obj.players.keys():
		player = game_obj.players[p]
		player_number = p
		username = player.name
		winner = (game_obj.winner == player)
		rating_pre = player.rating_pre
		rating_post = player.rating_post

		username_check = Player.objects.filter(username=username).exists()
		if username_check:
			username_id = Player.objects.get(username=username)
		else:
			username_id = Player(username=username)
			username_id.save()

		added_player = GamePlayerRelation(player_number=player_number,winner=winner,
											rating_pre=rating_pre,rating_post=rating_post,
											game=added_game,player=username_id)
		added_player.save()

		for mon in list(player.active_mons.values()):
			species = mon.species
			unique_species = normalize_name(species)
			species_id = Pokemon.objects.get(pokemon_unique_name=unique_species)
			used = True
			lead = False
			if species in player.lead:
				lead = True

			tera_type_id = None
			if mon.tera_type != None:
				tera_type_id = Type.objects.get(type_name=mon.tera_type.lower())

			pokemon_id = PokemonUsage(pokemon=species_id,used=used,lead=lead,
										game_player=added_player,tera_type=tera_type_id)
			pokemon_id.save()

			for move in mon.moveset:
				unique_move = normalize_name(move)
				if "g-max" in unique_move or "z-" in unique_move:
					continue
				if unique_move == 'vise-grip':
					unique_move = 'vice-grip'

				move_id = Move.objects.get(move_unique_name=unique_move)
				added_move = MoveUsage(move=move_id,pokemon=pokemon_id)
				added_move.save()

		for mon in player.team:
			print("adding unused mons")
			if "-*" in mon:
				continue
			if mon in player.used:
				continue

			unique_species = normalize_name(mon)
			species_id = Pokemon.objects.get(pokemon_unique_name=unique_species)
			used = False
			lead = False
			tera_type_id = None

			pokemon_id = PokemonUsage(pokemon=species_id,used=used,lead=lead,
										game_player=added_player,tera_type=tera_type_id)
			pokemon_id.save()

	return 1

def add_game_and_team_from_link(game,team):
	game_check = Game.objects.filter(link=game).exists()
	if game_check:
		# Connect user to game submission, no need to upload game again
		print("Game already in db")
		return 0

	log = get_game_from_link(game)
	game_log = log.split('\n')
	game_obj = parse_game(game_log)

	if not game_obj.valid:
		print("Game is invalid")
		return 0

	# Add game

	# Get game format
	tier_check = Tier.objects.filter(generation=game_obj.generation,tier_name=game_obj.tier).exists()

	# Make format if missing
	if tier_check:
		tier = Tier.objects.get(generation=game_obj.generation,tier_name=game_obj.tier)
	else:
		# UPDATE MODEL TO ACCEPT UNCATEGORIZED STYLE FOR NEW FORMAT, also change valid default to False
		tier = Tier(generation=game_obj.generation,tier_name=game_obj.tier,tier_display_name=game_obj.tier,
							style='VGC',valid=False)
		tier.save()

	time = dt.datetime.fromtimestamp(game_obj.start_time)
	added_game = Game(start_time=time,link=game,tier=tier,
						public=False,ranked=game_obj.ranked)
	added_game.save()

	for p in game_obj.players.keys():
		player = game_obj.players[p]
		player_number = p
		username = player.name
		winner = (game_obj.winner == player)
		rating_pre = player.rating_pre
		rating_post = player.rating_post

		username_check = Player.objects.filter(username=username).exists()
		if username_check:
			username_id = Player.objects.get(username=username)
		else:
			username_id = Player(username=username)
			username_id.save()

		added_player = GamePlayerRelation(player_number=player_number,winner=winner,
											rating_pre=rating_pre,rating_post=rating_post,
											game=added_game,player=username_id)
		added_player.save()

		for mon in list(player.active_mons.values()):
			species = mon.species
			unique_species = normalize_name(species)
			species_id = Pokemon.objects.get(pokemon_unique_name=unique_species)
			used = True
			lead = False
			if species in player.lead:
				lead = True

			tera_type_id = None
			if mon.tera_type != None:
				tera_type_id = Type.objects.get(type_name=mon.tera_type.lower())

			pokemon_id = PokemonUsage(pokemon=species_id,used=used,lead=lead,
										game_player=added_player,tera_type=tera_type_id)
			pokemon_id.save()

			for move in mon.moveset:
				unique_move = normalize_name(move)
				if "g-max" in unique_move or "z-" in unique_move:
					continue
				if unique_move == 'vise-grip':
					unique_move = 'vice-grip'

				move_id = Move.objects.get(move_unique_name=unique_move)
				added_move = MoveUsage(move=move_id,pokemon=pokemon_id)
				added_move.save()

		for mon in player.team:
			print("adding unused mons")
			if "-*" in mon:
				continue
			if mon in player.used:
				continue

			unique_species = normalize_name(mon)
			species_id = Pokemon.objects.get(pokemon_unique_name=unique_species)
			used = False
			lead = False
			tera_type_id = None

			pokemon_id = PokemonUsage(pokemon=species_id,used=used,lead=lead,
										game_player=added_player,tera_type=tera_type_id)
			pokemon_id.save()

	return 1