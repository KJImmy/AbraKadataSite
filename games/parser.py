class Field:
	def __init__(self):
		self.weather = None
		self.terrain = None
		self.trick_room = False
		self.positions = {}
		#Screens

neutral_field = Field()

class Game:
	def __init__(self,field=neutral_field):
		self.link = None
		self.players = {}
		self.field = field
		self.log = []
		self.current_turn = 0
		self.start_time = None
		self.tier = None
		self.generation = None
		self.ranked = False
		self.last_move = None
		self.moves_used = []
		self.valid = True
		self.winner = None

class Player:
	def __init__(self,name):
		self.name = name
		self.preview = []
		self.team = []
		self.used = []
		self.lead = []
		self.active_mons = {}
		self.rating_pre = None
		self.rating_post = None

	def __str__(self):
		return f"{self.name}"

class Pokemon:
	def __init__(self,nickname,species):
		self.nickname = nickname
		self.species = species
		self.stages = {"atk":0,"def":0,"spatk":0,"spdef":0,"speed":0}
		self.moveset = []
		self.current_percent_HP = 100
		self.on_field = False
		self.tera_type = None

	def __str__(self):
		return f"{self.nickname}: {self.species}"

class Move:
	def __init__(self,name,user):
		self.name = name
		self.user = user
		self.targets = []
		self.damage = {}

	def __str__(self):
		return f"{self.name}"

class Turn:
	def __init__(self,turn_number):
		self.turn_number = turn_number

def tokenize_line(line):
	line = line.strip()
	tokens = line.split('|')
	while "" in tokens:
		tokens.remove("")
	return tokens

def gender_bullshit(pokemon):
	tokens = pokemon.split(', ')
	species = tokens[0]

	if species == 'Indeedee-F':
		species = 'Indeedee-Female'
	elif species == 'Indeedee':
		species = 'Indeedee-Male'
	elif species == 'Meowstic-F':
		species = 'Meowstic-Female'
	elif species == 'Meowstic':
		species = 'Meowstic-Male'
	elif species == 'Oinkologne-F':
		species = 'Oinkologne-Female'
	elif species == 'Oinkologne':
		species = 'Oinkologne-Male'
	elif species == 'Basculegion-F':
		species = 'Basculegion-Female'
	elif species == 'Basculegion':
		species = 'Basculegion-Male'

	elif species == 'Enamorus':
		species = 'Enamorus-Incarnate'
	elif species == 'Landorus':
		species = 'Landorus-Incarnate'
	elif species == 'Thundurus':
		species = 'Thundurus-Incarnate'
	elif species == 'Tornadus':
		species = 'Tornadus-Incarnate'
	elif species == 'Toxtricity':
		species = 'Toxtricity-Amped'
	elif species == 'Oricorio':
		species = 'Oricorio-Baile'
	elif species == 'Meloetta':
		species = 'Meloetta-Aria'

	elif 'Alcremie' in species:
		species = 'Alcremie'
	elif 'Tatsugiri' in species:
		species = 'Tatsugiri'
	elif 'Maushold' in species:
		species = 'Maushold'
	elif 'Vivillon' in species:
		species = 'Vivillon'
	elif 'Gastrodon' in species:
		species = 'Gastrodon'
	elif 'Shellos' in species:
		species = 'Shellos'
	elif 'Dudunsparce' in species:
		species = 'Dudunsparce'
	elif 'Florges' in species:
		species = 'Florges'
	elif 'Floette' in species:
		spceies = 'Floette'
	elif 'Polteageist' in species:
		species = 'Polteageist'
	elif 'Sinistea' in species:
		species = 'Polteageist'
	elif 'Sawsbuck' in species:
		species = 'Sawsbuck'
	elif 'Deerling' in species:
		species = 'Deerling'
	elif 'Xerneas' in species:
		species = 'Xerneas'
	elif 'Pikachu' in species:
		species = 'Pikachu'

	elif species == 'Arceus-*':
		species = 'Arceus'
	elif species == 'Silvally-*':
		species = 'Silvally'

	elif 'Genesect' in species:
		species = 'Genesect'

	return species

def get_arceus_plate(pokemon):
	plate_types = {
		'Normal':'Blank Plate',
		'Dragon':'Draco Plate',
		'Dark':'Dread Plate',
		'Ground':'Earth Plate',
		'Fighting':'Fist Plate',
		'Fire':'Flame Plate',
		'Ice':'Icicle Plate',
		'Bug':'Insect Plate',
		'Psychic':'Mind Plate',
		'Fairy':'Pixie Plate',
		'Flying':'Sky Plate',
		'Water':'Splash Plate',
		'Ghost':'Spooky Plate',
		'Rock':'Stone Plate',
		'Poison':'Toxic Plate',
		'Electric':'Zap Plate'
	}
	typing = pokemon.split('-')[1]
	return plate_types[typing]

def remove_ambiguity(game,player,species):
	ambiguous_mons = ['Urshifu','Arceus','Zacian','Zamazenta','Genesect','Pumpkaboo','Gourgeist','Silvally']
	item = None

	for mon in ambiguous_mons:
		if mon in species:
			
			if 'Arceus-' in species:
				item = get_arceus_plate(species)
				species = 'Arceus'
				break
			elif 'Silvally-' in species:
				split = species.split('-')
				item = split[1]+" Memory"
				species = split[0]
				break
			elif 'Genesect-' in species:
				split = species.split('-')
				item = split[1]+" Drive"
				species = split[0]
				break

			elif species == 'Urshifu':
				species = 'Urshifu-Single-Strike'
			elif species == 'Gourgeist':
				species = 'Gourgeist-Average'
			elif species == 'Pumpkaboo':
				species = 'Pumpkaboo-Average'
			elif species == 'Zacian-Crowned':
				item = 'Rusted Sword'
			elif species == 'Zamazenta-Crowned':
				item = 'Rusted Shield'

			for i in range(len(game.players[player].preview)):
				if mon in game.players[player].preview[i]:
					game.players[player].preview[i] = species

	return game,species,item

def get_game_tier(tokens):
	tier = tokens[1]
	tier = tier.lower()
	tier = tier.replace(" ","")
	return tier

def get_player_number(player):
	p = player.split(": ")[0]
	p = p.replace("a","").replace("b","").replace("p","").replace("[of] ","")
	return int(p)

def make_player(game,tokens):
	#|player|p1|supermario98|drayden|
	player = get_player_number(tokens[1])
	if player in game.players.keys():
		return game
	username = tokens[2]
	if "'" in username:
		new_username = ""
		username_check = username.split("'")
		for i in range(len(username_check)):
			new_username += username_check[i]
			if i < len(username_check)-1:
				new_username += "''"
		username = new_username
	game.players[player] = Player(username)
	return game

def get_tier(game,tokens):
	tier = tokens[1].split('] ',1)[1]
	tier = tier.lower()
	tier = tier.replace(" ","")
	game.tier = tier
	return game

def get_preview_pokemon(game,tokens):
	illegal_mons = ['Aurumoth','Mollux','Fidgit','Equilibra','Astrolotl','Pajantom','Cawmodore','Voodoom','Plasmanta']
	player = get_player_number(tokens[1])
	pokemon = gender_bullshit(tokens[2])
	game.players[player].preview.append(pokemon)
	game.players[player].team.append(pokemon)
	if "Zoroark" in pokemon or "Zorua" in pokemon:
		game.valid = False
	if pokemon == 'Aurumoth':
		game.valid = False
		print(pokemon)
	if pokemon in illegal_mons:
		game.valid = False
	return game

def get_field_position(player):
	p = player.split(": ")[0]
	p = p.replace("p","").replace("[of] ","")
	return p	

def pokemon_switch_in(game,tokens):
	# |switch|p1a: Farigiraf|Farigiraf, L50, F|100/100
	player = get_player_number(tokens[1])
	nickname = tokens[1].split(': ',1)[1]
	species = gender_bullshit(tokens[2])
	current_percent_HP = tokens[3].split('/')[0]
	position = get_field_position(tokens[1])

	if nickname not in game.players[player].active_mons.keys():
		ra = remove_ambiguity(game,player,species)
		game = ra[0]
		species = ra[1]
		pokemon_info = tokens[2].split(', ')
		pokemon = Pokemon(nickname,species)
		pokemon.item = ra[2]
		if len(pokemon_info) > 1:
			if isinstance(pokemon_info[1],int):
				pokemon.level = int(pokemon_info[1].replace('L',''))
			else:
				pokemon.level = 100
		else:
			pokemon.level = 100
		game.players[player].used.append(species)
		game.players[player].active_mons[nickname] = pokemon

		if game.current_turn == 0:
			game.players[player].lead.append(species)

	game.field.positions[position] = game.players[player].active_mons[nickname]
	game.players[player].active_mons[nickname].on_field = True
	game.players[player].active_mons[nickname].current_percent_HP = current_percent_HP
	return game

def get_move(game,tokens):
	# |move|p1b: Iron Hands|Fake Out|p2a: Arcanine
	player = get_player_number(tokens[1])
	nickname = tokens[1].split(': ',1)[1]
	move_name = tokens[2]
	if move_name == "Vise Grip":
		move_name = "Vice Grip"
	pokemon = game.players[player].active_mons[nickname].moveset
	if move_name not in game.players[player].active_mons[nickname].moveset:
		game.players[player].active_mons[nickname].moveset.append(move_name)
	move = Move(move_name,pokemon)
	game.moves_used.append(move)
	game.last_move = move
	return game

def get_link(game,tokens):
	invalid_games = [	'https://replay.pokemonshowdown.com/gen9ou-1798817696',
						'https://replay.pokemonshowdown.com/gen9ou-1772079441',
						'https://replay.pokemonshowdown.com/gen9ou-1798815367']
	game.link = tokens[1]
	if "china-" in game.link or "radicalred" in game.link or game.link in invalid_games:
		game.valid = False
	return game

def get_winner(game,tokens):
	username = tokens[1]
	if "'" in username:
		new_username = ""
		username_check = username.split("'")
		for i in range(len(username_check)):
			new_username += username_check[i]
			if i < len(username_check)-1:
				new_username += "''"
		username = new_username
	if username == game.players[1].name:
		game.winner = game.players[1]
	elif username == game.players[2].name:
		game.winner = game.players[2]
	else:
		print("Winner's username does not match either player's")
		print(game.link)
		game.valid = False
	return game

def get_ratings(game,tokens):
	# |raw|aaam's rating: 1133 &rarr; <strong>1162</strong><br />(+29 for winning)
	if "'s rating: " not in tokens[1]:
		return game
	info = tokens[1].split("'s rating: ")
	username = info[0]
	ratings = info[1].split(" &rarr; <strong>")
	rating_pre = ratings[0]
	rating_post = ratings[1].split("</strong")[0]
	for player in list(game.players.values()):
		if player.name == username:
			player.rating_pre = rating_pre
			player.rating_post = rating_post
	return game

def get_tera_type(game,tokens):
	player = get_player_number(tokens[1])
	nickname = tokens[1].split(": ",1)[1]
	tera_type = tokens[2]
	game.players[player].active_mons[nickname].tera_type = tera_type
	return game

def parse_game(game_log):
	game = Game()

	for line in game_log:
		tokens = tokenize_line(line)

		if len(tokens) == 0:
			continue

		#Game Info
		if tokens[0] == 'link':
			game = get_link(game,tokens)
		elif tokens[0] == 't:' and game.current_turn == 0:
			game.start_time = int(tokens[1])
		elif tokens[0] == 'gen':
			game.generation = tokens[1]
		elif tokens[0] == 'tier':
			game = get_tier(game,tokens)
		elif tokens[0] == 'rated':
			game.ranked = True
		elif tokens[0] == 'win':
			game = get_winner(game,tokens)

		elif tokens[0] == 'player':
			game = make_player(game, tokens)
		elif tokens[0] == 'raw':
			game = get_ratings(game,tokens)

		elif tokens[0] == 'poke':
			game = get_preview_pokemon(game,tokens)
		elif tokens[0] == 'switch' or tokens[0] == 'drag':
			game = pokemon_switch_in(game,tokens)
		elif tokens[0] == '-terastallize':
			game = get_tera_type(game,tokens)

		elif tokens[0] == 'move':
			game = get_move(game,tokens)

		elif tokens[0] == 'turn':
			game.current_turn+=1

		elif tokens[0] == '-end':
			if len(tokens) > 2:
				if tokens[2] == 'Illusion':
					game.valid = False



		#Stop parsing invalid games
		if game.valid == False:
			return game
	
	if game.current_turn == 0 or game.current_turn == 1:
		game.valid = False

	return game