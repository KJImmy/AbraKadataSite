import requests

from django.db import connection

from games.models import Game,GamePlayerRelation,PokemonUsage,Player

def validate_username(username,link1,link2):
	check1 = False
	check2 = False
	opponent1 = ""
	opponent2 = ""
	opponent_check = False
	final_check = False

	public_games = list(Game.objects.filter(public=True).values_list('link',flat=True))
	if link1[-4:] == ".log":
		link1 = link1[:-4]
	if link2[-4:] == ".log":
		link2 = link2[:-4]

	if link1 in public_games or link2 in public_games:
		return (final_check,"Please only submit private replays")

	if link1 == link2:
		return (final_check,"Please submit two distinct games")

	if link1[-4:] != ".log":
		link1+=".log"
	if link2[-4:] != ".log":
		link2+=".log"

	log1 = requests.get(link1).text
	log2 = requests.get(link2).text

	loopable_log1 = log1.split('\n')
	for line in loopable_log1:
		tokens = line.split('|')
		if len(tokens) < 2:
			continue
		if tokens[1] == "player" and len(tokens) > 3:
			print(tokens[3])
			if username == tokens[3]:
				check1 = True
			else:
				opponent1 = tokens[3]

	if not check1:
		return (final_check,"No matching username in game 1")

	loopable_log2 = log2.split('\n')
	for line in loopable_log2:
		tokens = line.split('|')
		if len(tokens) < 2:
			continue
		if tokens[1] == "player" and len(tokens) > 3:
			if username == tokens[3]:
				check2 = True
			else:
				opponent2 = tokens[3]

	if not check2:
		return (final_check,"No matching username in game 2")

	if opponent1 != opponent2:
		opponent_check = True

	if not opponent_check:
		return (final_check,"Please submit games against 2 distinct players")

	if check1 and check2 and opponent_check:
		final_check = True

	return (final_check,f"{username} is now connected to your account")

# def get_user_teams(user):
# 	player_ids = Player.objects.filter(site_user__isnull=False).filter(site_user=user.id).values_list('id',flat=True)
# 	unassigned_games = GamePlayerRelation.objects.filter(player__in=player_ids).filter(user_team__isnull=True)

# 	current_teams = user.team_of_user.all()

# 	# with connection.cursor() as cursor:
# 	# 	cursor.execute("SELECT pokemon1,pokemon2,pokemon3,pokemon4,pokemon5,pokemon6,COUNT(*) AS total_games,\
# 	# 						COUNT(*) FILTER (WHERE p.winner = true) AS total_wins,tier_id \
# 	# 					FROM crosstab(\
# 	# 						'SELECT game_player_id,mon.id,pokemon_id \
# 	# 						FROM games_pokemonusage mon \
# 	# 						LEFT JOIN games_gameplayerrelation player \
# 	# 						ON mon.game_player_id = player.id \
# 	# 						LEFT JOIN games_game game \
# 	# 						ON game.id = player.game_id \
# 	# 						WHERE player.player_id in %s \
# 	# 						ORDER BY 1,3') \
# 	# 					AS ct (player BIGINT, pokemon1 BIGINT, pokemon2 BIGINT,\
# 	# 						pokemon3 BIGINT, pokemon4 BIGINT, pokemon5 BIGINT, pokemon6 BIGINT)\
# 	# 					LEFT JOIN games_gameplayerrelation p ON p.id = ct.player \
# 	# 					LEFT JOIN games_game g ON p.game_id = g.id \
# 	# 					GROUP BY pokemon1,pokemon2,pokemon3,pokemon4,pokemon5,pokemon6,tier_id \
# 	# 					ORDER BY total_games DESC",[tuple(player_ids)])
# 	# 	query = cursor.fetchall()



# 	results = {}
# 	for q in query:
# 		if q[8] not in results.keys():
# 			results[q[8]] = {}
# 		team_list = q[:6]
# 		team = Pokemon.objects.filter(id__in=team_list)
# 		results[q[8]][team] = {'Played':q[6],'Winrate':round(q[7]/q[6]*100,2)}