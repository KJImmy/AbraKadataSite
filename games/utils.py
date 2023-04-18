import requests
import datetime as dt

from .models import Game,GamePlayerRelation,PokemonUsage,MoveUsage,Player
from .parser import parse_game
from tiers.models import Tier
from pokemon.models import Pokemon,Type,Move

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

def get_game_from_link(game):
	if game[-4:] != ".log":
		game+=".log"

	log = requests.get(game).text

	return log

def add_game_from_link(game):
	game_check = Game.objects.filter(link=game).exists()
	if game_check:
		# Connect user to game submission, no need to upload game again
		print("Game already in db")
		return 0

	log = get_game_from_link(game)
	game_log = log.split('\n')
	game_obj = parse_game(game_log)

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

