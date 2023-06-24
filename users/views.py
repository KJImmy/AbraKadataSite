import operator
import json

from django.shortcuts import render,redirect
from django.urls import reverse
from django.db import connection

from .forms import ShowdownUsernameForm,SubmitGameForm,CustomUserCreationForm,ChangeEmailForm,PokemonForm
from .models import PokemonOnTeam,UserTeam
from .utils import validate_username
from games.utils import add_game_from_link
from games.models import Player,GamePlayerRelation,PokemonUsage,Game
from pokemon.models import Pokemon,Move,Type
from tiers.models import Tier
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.middleware import get_user

# Create your views here.
def dashboard_view(request):
	context = {}
	return render(request,"users/dashboard.html",context)

def stats_view(request):
	ranked_bool = True

	user = get_user(request)
	player = Player.objects.filter(site_user__isnull=False).filter(site_user=user.id)
	player_ids = []
	game_list = []
	show_ids = player

	results = {}
	for p in player:
		player_ids.append(p.id)
		# Go through all instances of player's games
		for t in p.games_of_player.all():
			game_list.append(t.id)
			# Get formats in which games were played
			cur_tier = t.game.tier
			if cur_tier not in results.keys():
				results.update({cur_tier:{}})

			# Get team that was played
			cur_team = t.pokemon_of_player.all()
			team = []
			team_ids = []
			for p in cur_team:
				team.append(p.pokemon)
				team_ids.append(p.pokemon.id)
			team.sort(key=operator.attrgetter('pk'))
			tt = tuple(team)
			if tt not in results[cur_tier].keys():
				results[cur_tier].update({tt:{	"team_ids":team_ids,
												"Won":0,
												"Played":0,
												"Winrate":None,
												"game_list":[]}})
			results[cur_tier][tt]["game_list"].append(t.id)
			results[cur_tier][tt]["Played"] += 1
			if t.winner == True:
				results[cur_tier][tt]["Won"] += 1

	tiers_played = results.keys()

	if player_ids == []:
		return redirect(reverse("psusername"))
	else:
		# Calc winrates
		for tier in results.keys():
			for team in results[tier].keys():
				results[tier][team]["Winrate"] = round(results[tier][team]["Won"] * 100 / results[tier][team]["Played"],2)

		general_stats = Pokemon.objects.raw('	SELECT mon.pokemon_id AS id,game.tier_id,\
													c.count AS games_in_tier,\
													ROUND(CAST(COUNT(*) AS DECIMAL) * 100 / CAST(c.count AS DECIMAL),2) AS appearance_rate,\
													ROUND(CAST(COUNT(*) FILTER (WHERE mon.used = true) AS DECIMAL) * 100 / CAST(COUNT(*) AS DECIMAL),2) AS used_rate,\
													ROUND(CAST(COUNT(*) FILTER (WHERE mon.lead = true) AS DECIMAL) * 100 / CAST(COUNT(*) AS DECIMAL),2) AS lead_rate,\
													ROUND(CAST(COUNT(*) FILTER (WHERE player.winner = true) AS DECIMAL) * 100 / CAST(COUNT(*) AS DECIMAL),2) AS winrate,\
													ROUND(CAST(COUNT(*) FILTER (WHERE mon.used = true AND player.winner = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(*) FILTER (WHERE mon.used = true) AS DECIMAL),0),2) AS winrate_used,\
													ROUND(CAST(COUNT(*) FILTER (WHERE mon.lead = true AND player.winner = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(*) FILTER (WHERE mon.lead = true) AS DECIMAL),0),2) AS winrate_lead,\
													ROUND(CAST(COUNT(*) FILTER (WHERE mon.dynamaxed = true) AS DECIMAL) * 100 / CAST(COUNT(*) AS DECIMAL),2) AS dynamax_frequency,\
													ROUND(CAST(COUNT(*) FILTER (WHERE mon.dynamaxed = true AND player.winner = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(*) FILTER (WHERE mon.dynamaxed = true) AS DECIMAL),0),2) AS dynamax_winrate,\
													ROUND(CAST(COUNT(*) FILTER (WHERE mon.tera_type_id IS NOT NULL) AS DECIMAL) * 100 / CAST(COUNT(*) AS DECIMAL),2) AS tera_frequency \
												FROM games_pokemonusage mon \
												INNER JOIN games_gameplayerrelation player \
												ON mon.game_player_id = player.id \
												INNER JOIN games_game game \
												ON game.id = player.game_id \
												LEFT JOIN (	SELECT cg.tier_id,COUNT(*) \
															FROM games_gameplayerrelation cp \
															INNER JOIN games_game cg \
															ON cg.id = cp.game_id \
															WHERE cp.player_id IN %s \
															GROUP BY cg.tier_id) c \
												ON c.tier_id = game.tier_id \
												WHERE player.player_id IN %s \
												GROUP BY mon.pokemon_id,game.tier_id,c.count',[tuple(player_ids),tuple(player_ids)])

		overall_tier_stats = Tier.objects.raw('	SELECT game.tier_id AS id,\
													COUNT(*) AS game_count,\
													ROUND(CAST(COUNT(*) FILTER (WHERE player.winner = true) AS DECIMAL) * 100 / CAST(COUNT(*) AS DECIMAL),2) AS winrate \
												FROM games_gameplayerrelation player \
												INNER JOIN games_game game \
												ON game.id = player.game_id \
												WHERE player.player_id IN %s \
												GROUP BY game.tier_id \
												ORDER BY game_count DESC',[tuple(player_ids)])

		context = {
			'results':results,
			'general':general_stats,
			'tiers':tiers_played,
			'tier_stats':overall_tier_stats,
			'ids':show_ids
		}
		return render(request,"users/user_stats.html",context)


def stats_view_new(request):
	user = get_user(request)
	player_ids = Player.objects.filter(site_user__isnull=False).filter(site_user=user.id).values_list('id',flat=True)
	
	with connection.cursor() as cursor:
		cursor.execute("SELECT pokemon1,pokemon2,pokemon3,pokemon4,pokemon5,pokemon6,COUNT(*) AS total_games,\
							COUNT(*) FILTER (WHERE p.winner = true) AS total_wins,tier_id \
						FROM crosstab(\
							'SELECT game_player_id,mon.id,pokemon_id \
							FROM games_pokemonusage mon \
							LEFT JOIN games_gameplayerrelation player \
							ON mon.game_player_id = player.id \
							LEFT JOIN games_game game \
							ON game.id = player.game_id \
							WHERE player.player_id in %s \
							ORDER BY 1,3') \
						AS ct (player BIGINT, pokemon1 BIGINT, pokemon2 BIGINT,\
							pokemon3 BIGINT, pokemon4 BIGINT, pokemon5 BIGINT, pokemon6 BIGINT)\
						LEFT JOIN games_gameplayerrelation p ON p.id = ct.player \
						LEFT JOIN games_game g ON p.game_id = g.id \
						GROUP BY pokemon1,pokemon2,pokemon3,pokemon4,pokemon5,pokemon6,tier_id \
						ORDER BY total_games DESC",[tuple(player_ids)])
		query = cursor.fetchall()

	results = {}
	for q in query:
		if q[8] not in results.keys():
			results[q[8]] = {}
		team_list = q[:6]
		team = Pokemon.objects.filter(id__in=team_list)
		results[q[8]][team] = {'Played':q[6],'Winrate':round(q[7]/q[6]*100,2)}

	tiers_played = Tier.objects.raw("SELECT tier_id FROM games_game g LEFT JOIN games_gameplayerrelation p ON p.game_id = g.id \
										WHERE p.player_id IN %s",[tuple(player_ids)])

	overall_tier_stats = Tier.objects.raw('	SELECT game.tier_id AS id,\
												COUNT(*) AS game_count,\
												ROUND(CAST(COUNT(*) FILTER (WHERE player.winner = true) AS DECIMAL) * 100 / CAST(COUNT(*) AS DECIMAL),2) AS winrate \
											FROM games_gameplayerrelation player \
											INNER JOIN games_game game \
											ON game.id = player.game_id \
											WHERE player.player_id IN %s \
											GROUP BY game.tier_id \
											ORDER BY game_count DESC',[tuple(player_ids)])

	context = {
		'results':results,
		'tiers':tiers_played,
		'tier_stats':overall_tier_stats
	}
	return render(request,"users/user_stats.html",context)

def breakdown_view_new(request):
	user = get_user(request)
	player_ids = Player.objects.filter(site_user__isnull=False).filter(site_user=user.id).values_list('id',flat=True)
	game = None
	response = None
	if request.method == "POST":
		response = request.POST
		team_ids = [s for s in response['team'].replace('[','').replace(']','').split(',')]
		team_ids = team_ids[:-1]
		team_ids = [int(s) for s in team_ids]

		if 'game' in response.keys():
			game_id = int(response['game'].replace('[','').replace(']',''))
			game = GamePlayerRelation.objects.get(pk=game_id)
			game.personal_include = not game.personal_include
			game.save()

	team = Pokemon.objects.filter(pk__in=team_ids)

	with connection.cursor() as cur:
		cur.execute("	SELECT a.id \
						FROM games_gameplayerrelation a \
						INNER JOIN ( \
							SELECT p_b.id \
							FROM games_gameplayerrelation p_b \
							LEFT JOIN games_pokemonusage m_b \
							ON p_b.id = m_b.game_player_id \
							WHERE pokemon_id IN %s \
							AND p_b.player_id IN %s \
							AND p_b.personal_include = True \
							GROUP BY p_b.id \
							HAVING COUNT(*) = %s \
							AND (SELECT COUNT(*) FROM games_pokemonusage m_c WHERE m_c.game_player_id = p_b.id) = %s \
						) b on a.id = b.id",
						[tuple(team_ids),tuple(player_ids),len(team_ids),len(team_ids)])
		game_query = cur.fetchall()
		game_ids = []
		for g in game_query:
			game_ids.append(g[0])

		cur.execute('	SELECT ROUND(CAST(COUNT(*) FILTER (WHERE player.winner = true) AS DECIMAL) * 100 / CAST(COUNT(*) AS DECIMAL),2) AS winrate \
						FROM games_gameplayerrelation player \
						WHERE player.id IN %s',[tuple(game_ids)])
		winrate = cur.fetchone()[0]
		winrate = float(winrate)

		cur.execute("	SELECT a.id \
						FROM games_gameplayerrelation a \
						INNER JOIN ( \
							SELECT p_b.id \
							FROM games_gameplayerrelation p_b \
							LEFT JOIN games_pokemonusage m_b \
							ON p_b.id = m_b.game_player_id \
							WHERE pokemon_id IN %s \
							AND p_b.player_id IN %s \
							GROUP BY p_b.id \
							HAVING COUNT(*) = %s \
							AND (SELECT COUNT(*) FROM games_pokemonusage m_c WHERE m_c.game_player_id = p_b.id) = %s \
						) b on a.id = b.id",
						[tuple(team_ids),tuple(player_ids),len(team_ids),len(team_ids)])
		game_query = cur.fetchall()
		full_game_list = []
		for g in game_query:
			full_game_list.append(g[0])

	all_games = GamePlayerRelation.objects.filter(pk__in=full_game_list)

	# Identify user teams that use the same 6 mons
	user_teams = UserTeam.objects.raw("	SELECT a.id \
										FROM users_userteams a \
										INNER JOIN ( \
											SELECT t_b.id \
											FROM users_userteams t_b \
											LEFT JOIN users_pokemononteam m_b \
											ON t_b.id = m_b.game_player_id \
											WHERE pokemon_id IN %s \
											AND t_b.site_user_ud IN %s \
											GROUP BY t_b.id \
											HAVING COUNT(*) = %s \
											AND (SELECT COUNT(*) FROM games_pokemonusage m_c WHERE m_c.game_player_id = t_b.id) = %s \
										) b on a.id = b.id",
										[tuple(team_ids),user.id,len(team_ids),len(team_ids)])

	individual_usage = Pokemon.objects.raw('	SELECT mon.pokemon_id AS id,\
													ROUND(CAST(COUNT(*) FILTER (WHERE player.winner = true) AS DECIMAL) * 100 / CAST(COUNT(*) AS DECIMAL),2) AS winrate,\
													ROUND(CAST(COUNT(*) FILTER (WHERE player.winner = true AND mon.used = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(*) FILTER (WHERE mon.used = true) AS DECIMAL),0),2) AS winrate_used,\
													ROUND(CAST(COUNT(*) FILTER (WHERE player.winner = true AND mon.lead = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(*) FILTER (WHERE mon.lead = true) AS DECIMAL),0),2) AS winrate_lead,\
													ROUND(CAST(COUNT(*) FILTER (WHERE mon.used = true) AS DECIMAL) * 100 / CAST(%s AS DECIMAL),2) AS frequency_used,\
													ROUND(CAST(COUNT(*) FILTER (WHERE mon.lead = true) AS DECIMAL) * 100 / CAST(%s AS DECIMAL),2) AS frequency_lead\
												FROM games_pokemonusage mon \
												INNER JOIN games_gameplayerrelation player \
												ON mon.game_player_id = player.id \
												WHERE player.id IN %s \
												GROUP BY mon.pokemon_id',[len(game_ids),len(game_ids),tuple(game_ids)])

	moves = Move.objects.raw('	SELECT move_id AS id,\
									mon.pokemon_id AS pokemon,\
									ROUND(CAST(COUNT(*) FILTER (WHERE player.winner = true) AS DECIMAL) * 100 / CAST(COUNT(*) AS DECIMAL),2) AS winrate,\
									ROUND(CAST(COUNT(*) AS DECIMAL) * 100 / CAST(c.count AS DECIMAL),2) AS move_frequency \
								FROM games_moveusage m \
								INNER JOIN games_pokemonusage mon ON m.pokemon_id = mon.id \
								INNER JOIN games_gameplayerrelation player ON mon.game_player_id = player.id \
								LEFT JOIN pokemon_move move ON m.move_id = move.id \
								LEFT JOIN (	SELECT mon_c.pokemon_id, COUNT(*) FILTER (WHERE mon_c.used = true) \
											FROM games_pokemonusage mon_c \
											INNER JOIN games_gameplayerrelation player_c \
											ON mon_c.game_player_id = player_c.id \
											WHERE player_c.id IN %s \
											AND player_c.personal_include = true \
											GROUP BY mon_c.pokemon_id \
											) c ON c.pokemon_id = mon.pokemon_id \
								WHERE player.id IN %s \
								GROUP BY move_id,mon.pokemon_id,c.count',[tuple(game_ids),tuple(game_ids)])

	opponents = Pokemon.objects.raw('	SELECT opp_mon.pokemon_id AS id, mon.pokemon_id AS team_mon,\
											ROUND(CAST(COUNT(mon.pokemon_id) FILTER (WHERE player.winner = true) AS DECIMAL) * 100 / CAST(COUNT(opp_mon.pokemon_id) AS DECIMAL),2) AS winrate,\
											ROUND(CAST(COUNT(mon.pokemon_id) FILTER (WHERE player.winner = true AND mon.used = true AND opp_mon.used = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(mon.pokemon_id) FILTER (WHERE mon.used = true AND opp_mon.used = true) AS DECIMAL),0),2) AS winrate_used,\
											ROUND(CAST(COUNT(mon.pokemon_id) FILTER (WHERE player.winner = true AND mon.lead = true AND opp_mon.lead = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(mon.pokemon_id) FILTER (WHERE mon.lead = true AND opp_mon.lead = true) AS DECIMAL),0),2) AS winrate_lead,\
											ROUND(CAST(COUNT(mon.pokemon_id) FILTER (WHERE mon.used = true AND opp_mon.used = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(mon.pokemon_id) AS DECIMAL),0),2) AS faceoff_frequency,\
											ROUND(CAST(COUNT(mon.pokemon_id) FILTER (WHERE mon.lead = true AND opp_mon.lead = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(mon.pokemon_id) AS DECIMAL),0),2) AS faceoff_frequency_lead \
										FROM games_pokemonusage mon \
										INNER JOIN games_gameplayerrelation player ON player.id = mon.game_player_id \
										INNER JOIN games_gameplayerrelation opponent \
										ON opponent.game_id = player.game_id AND opponent.id <> player.id \
										INNER JOIN games_pokemonusage opp_mon ON opp_mon.game_player_id = opponent.id \
										WHERE player.id IN %s \
										AND player.personal_include = true \
										GROUP BY opp_mon.pokemon_id,mon.pokemon_id',[tuple(game_ids)])

	opponents_for_team = Pokemon.objects.raw('	SELECT mon.pokemon_id AS id,\
													ROUND(CAST(COUNT(mon.pokemon_id) FILTER (WHERE player.winner = true) AS DECIMAL) * 100 / CAST(COUNT(mon.pokemon_id) AS DECIMAL),2) AS winrate_against,\
													ROUND(CAST(COUNT(mon.pokemon_id) FILTER (WHERE player.winner = true AND mon.used = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(mon.pokemon_id) FILTER (WHERE mon.used = true) AS DECIMAL),0),2) AS winrate_against_used,\
													ROUND(CAST(COUNT(mon.pokemon_id) FILTER (WHERE player.winner = true AND mon.lead = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(mon.pokemon_id) FILTER (WHERE mon.lead = true) AS DECIMAL),0),2) AS winrate_against_lead,\
													ROUND(CAST(COUNT(mon.pokemon_id) FILTER (WHERE mon.used = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(mon.pokemon_id) AS DECIMAL),0),2) AS frequency_used,\
													ROUND(CAST(COUNT(mon.pokemon_id) FILTER (WHERE mon.lead = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(mon.pokemon_id) AS DECIMAL),0),2) AS frequency_lead \
												FROM games_pokemonusage mon \
												INNER JOIN games_gameplayerrelation opponent \
												ON opponent.id = mon.game_player_id \
												INNER JOIN games_gameplayerrelation player \
												ON player.game_id = opponent.game_id AND player.id <> opponent.id \
												WHERE player.id IN %s \
												AND player.personal_include = true \
												GROUP BY mon.pokemon_id',[tuple(game_ids)])

	context = {
		'winrate':winrate,
		'team':team,
		'individual':individual_usage,
		'moves':moves,
		'opponents':opponents,
		'opponents_for_team':opponents_for_team,
		'game_list':all_games,
		'games':game_ids,
		'all_games':full_game_list,
		'user_teams':user_teams
	}

	return render(request,"users/team_breakdown.html",context)

def register_view(request):
	if request.method == "GET":
		return render(
			request, "users/register.html",
			{"form": CustomUserCreationForm}
		)
	elif request.method == "POST":
		form = CustomUserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			return redirect(reverse("dashboard"))
		
		cleaned = form.errors.as_data()

		return render(
			request, "users/register.html",
			{"form": CustomUserCreationForm,
			"cleaned":cleaned})

def submit_showdown_name_view(request):
	response = request.POST

	context={
		'form': ShowdownUsernameForm,
		'response':response
	}
	if request.user.is_authenticated:
		user = get_user(request)
		username_list = Player.objects.filter(site_user=user)
		context['usernames'] = username_list

		if response:
			name = response['username']
			g1 = response['game1']
			g2 = response['game2']

			username_check = Player.objects.filter(username=name).exists()
			if not username_check:
				player = Player(username=name)
				player.save()
			else:
				player = Player.objects.get(username=name)

			if player.site_user:
				context['validation'] = (False,"This PS Username is already connected to an AK account")
				return render(request,'users/showdown_username.html',context)

			validation = validate_username(name,g1,g2)
			context['validation'] = validation

			if validation[0]:
				user = get_user(request)
				player.site_user = user
				player.save()

				add_game_from_link(g1)
				add_game_from_link(g2)

	return render(request,'users/showdown_username.html',context)

def submit_game_view(request):
	response = request.POST

	context = {
		'form':SubmitGameForm
	}

	if response and request.user.is_authenticated:
		link = response['game_link']
		context['link'] = link

		submit = add_game_from_link(link)
		context['submit'] = submit

	return render(request,'users/submit_game.html',context)

def change_email_view(request):
	response = request.POST
	user = get_user(request)

	context = {
		'form':ChangeEmailForm
	}

	if response and request.user.is_authenticated:
		new_email = response['email']
		context['new_email'] = new_email
		user.email = new_email
		user.save()


	context['cur_email'] = user.email

	return render(request,'registration/email_reset.html',context)

def teams_view(request):
	user = get_user(request)
	user_teams = UserTeam.objects.filter(site_user=user.id)

	context = {
		'teams':user_teams
	}

	if request.method == "POST":
		response = request.POST
		context['response'] = response
		if response['new_team']:
			new_team = UserTeam(site_user=user)
			new_team.save()
			return redirect(reverse("teambuilder",args=[new_team.id]))
			context['id'] = new_team.id

	return render(request,'users/teams.html',context)

def teambuilder_view(request,team):
	context = {
		"form":PokemonForm
	}
	return render(request,'users/teambuilder.html',context)





# def breakdown_view(request):
# 	included_game_ids = []
# 	if request.method == "POST":
# 		response = request.POST

# 		game_ids = response['games']
# 		game_list = [int(s) for s in game_ids.replace('[','').replace(']','').split(',')]
# 		team_ids  =	[int(s) for s in response['team'].replace('[','').replace(']','').split(',')]

# 		player_objects = GamePlayerRelation.objects.filter(id__in=game_list)
# 		team_objects = Pokemon.objects.filter(pk__in=team_ids)

# 		if 'include_game' in response.keys():
# 			included_game_ids = [int(s) for s in response.getlist('include_game')]
# 			for game in player_objects:
# 				if game.id in included_game_ids:
# 					game.personal_include = True
# 				elif game.id not in included_game_ids:
# 					game.personal_include = False
# 				game.save()


# 	with connection.cursor() as cur:
# 		cur.execute('	SELECT ROUND(CAST(COUNT(*) FILTER (WHERE player.winner = true) AS DECIMAL) * 100 / CAST(COUNT(*) AS DECIMAL),2) AS winrate \
# 						FROM games_gameplayerrelation player \
# 						WHERE player.id IN %s \
# 						AND player.personal_include = true',[tuple(game_list)])
# 		winrate = cur.fetchone()[0]
# 		winrate = float(winrate)

# 	individual_usage = Pokemon.objects.raw('	SELECT mon.pokemon_id AS id,\
# 													ROUND(CAST(COUNT(*) FILTER (WHERE player.winner = true) AS DECIMAL) * 100 / CAST(COUNT(*) AS DECIMAL),2) AS winrate,\
# 													ROUND(CAST(COUNT(*) FILTER (WHERE player.winner = true AND mon.used = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(*) FILTER (WHERE mon.used = true) AS DECIMAL),0),2) AS winrate_used,\
# 													ROUND(CAST(COUNT(*) FILTER (WHERE player.winner = true AND mon.lead = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(*) FILTER (WHERE mon.lead = true) AS DECIMAL),0),2) AS winrate_lead,\
# 													ROUND(CAST(COUNT(*) FILTER (WHERE mon.used = true) AS DECIMAL) * 100 / CAST(%s AS DECIMAL),2) AS frequency_used,\
# 													ROUND(CAST(COUNT(*) FILTER (WHERE mon.lead = true) AS DECIMAL) * 100 / CAST(%s AS DECIMAL),2) AS frequency_lead\
# 												FROM games_pokemonusage mon \
# 												INNER JOIN games_gameplayerrelation player \
# 												ON mon.game_player_id = player.id \
# 												WHERE player.id IN %s \
# 												AND player.personal_include = true \
# 												GROUP BY mon.pokemon_id',[len(game_list),len(game_list),tuple(game_list)])

# 	moves = Move.objects.raw('	SELECT move_id AS id,\
# 									mon.pokemon_id AS pokemon,\
# 									ROUND(CAST(COUNT(*) FILTER (WHERE player.winner = true) AS DECIMAL) * 100 / CAST(COUNT(*) AS DECIMAL),2) AS winrate,\
# 									ROUND(CAST(COUNT(*) AS DECIMAL) * 100 / CAST(c.count AS DECIMAL),2) AS move_frequency \
# 								FROM games_moveusage m \
# 								INNER JOIN games_pokemonusage mon ON m.pokemon_id = mon.id \
# 								INNER JOIN games_gameplayerrelation player ON mon.game_player_id = player.id \
# 								LEFT JOIN pokemon_move move ON m.move_id = move.id \
# 								LEFT JOIN (	SELECT mon_c.pokemon_id, COUNT(*) FILTER (WHERE mon_c.used = true) \
# 											FROM games_pokemonusage mon_c \
# 											INNER JOIN games_gameplayerrelation player_c \
# 											ON mon_c.game_player_id = player_c.id \
# 											WHERE player_c.id IN %s \
# 											AND player_c.personal_include = true \
# 											GROUP BY mon_c.pokemon_id \
# 											) c ON c.pokemon_id = mon.pokemon_id \
# 								WHERE player.id IN %s \
# 								AND player.personal_include = true \
# 								GROUP BY move_id,mon.pokemon_id,c.count',[tuple(game_list),tuple(game_list)])

# 	opponents = Pokemon.objects.raw('	SELECT opp_mon.pokemon_id AS id, mon.pokemon_id AS team_mon,\
# 											ROUND(CAST(COUNT(mon.pokemon_id) FILTER (WHERE player.winner = true) AS DECIMAL) * 100 / CAST(COUNT(opp_mon.pokemon_id) AS DECIMAL),2) AS winrate,\
# 											ROUND(CAST(COUNT(mon.pokemon_id) FILTER (WHERE player.winner = true AND mon.used = true AND opp_mon.used = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(mon.pokemon_id) FILTER (WHERE mon.used = true AND opp_mon.used = true) AS DECIMAL),0),2) AS winrate_used,\
# 											ROUND(CAST(COUNT(mon.pokemon_id) FILTER (WHERE player.winner = true AND mon.lead = true AND opp_mon.lead = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(mon.pokemon_id) FILTER (WHERE mon.lead = true AND opp_mon.lead = true) AS DECIMAL),0),2) AS winrate_lead,\
# 											ROUND(CAST(COUNT(mon.pokemon_id) FILTER (WHERE mon.used = true AND opp_mon.used = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(mon.pokemon_id) AS DECIMAL),0),2) AS faceoff_frequency,\
# 											ROUND(CAST(COUNT(mon.pokemon_id) FILTER (WHERE mon.lead = true AND opp_mon.lead = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(mon.pokemon_id) AS DECIMAL),0),2) AS faceoff_frequency_lead \
# 										FROM games_pokemonusage mon \
# 										INNER JOIN games_gameplayerrelation player ON player.id = mon.game_player_id \
# 										INNER JOIN games_gameplayerrelation opponent \
# 										ON opponent.game_id = player.game_id AND opponent.id <> player.id \
# 										INNER JOIN games_pokemonusage opp_mon ON opp_mon.game_player_id = opponent.id \
# 										WHERE player.id IN %s \
# 										AND player.personal_include = true \
# 										GROUP BY opp_mon.pokemon_id,mon.pokemon_id',[tuple(game_list)])

# 	opponents_for_team = Pokemon.objects.raw('	SELECT mon.pokemon_id AS id,\
# 													ROUND(CAST(COUNT(mon.pokemon_id) FILTER (WHERE player.winner = true) AS DECIMAL) * 100 / CAST(COUNT(mon.pokemon_id) AS DECIMAL),2) AS winrate_against,\
# 													ROUND(CAST(COUNT(mon.pokemon_id) FILTER (WHERE player.winner = true AND mon.used = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(mon.pokemon_id) FILTER (WHERE mon.used = true) AS DECIMAL),0),2) AS winrate_against_used,\
# 													ROUND(CAST(COUNT(mon.pokemon_id) FILTER (WHERE player.winner = true AND mon.lead = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(mon.pokemon_id) FILTER (WHERE mon.lead = true) AS DECIMAL),0),2) AS winrate_against_lead,\
# 													ROUND(CAST(COUNT(mon.pokemon_id) FILTER (WHERE mon.used = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(mon.pokemon_id) AS DECIMAL),0),2) AS frequency_used,\
# 													ROUND(CAST(COUNT(mon.pokemon_id) FILTER (WHERE mon.lead = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(mon.pokemon_id) AS DECIMAL),0),2) AS frequency_lead \
# 												FROM games_pokemonusage mon \
# 												INNER JOIN games_gameplayerrelation opponent \
# 												ON opponent.id = mon.game_player_id \
# 												INNER JOIN games_gameplayerrelation player \
# 												ON player.game_id = opponent.game_id AND player.id <> opponent.id \
# 												WHERE player.id IN %s \
# 												AND player.personal_include = true \
# 												GROUP BY mon.pokemon_id',[tuple(game_list)])

# 	opponent_types = Type.objects.raw('	SELECT type.id AS id, \
# 											ROUND(CAST(COUNT(*) FILTER (WHERE player.winner = true) AS DECIMAL) * 100 / CAST(COUNT(*) AS DECIMAL),2) AS winrate_against, \
# 											ROUND(CAST(COUNT(*) FILTER (WHERE player.winner = true AND mon.used = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(*) FILTER (WHERE mon.used = true) AS DECIMAL),0),2) AS winrate_against_used \
# 										FROM games_pokemonusage mon \
# 										INNER JOIN games_gameplayerrelation opponent \
# 										ON opponent.id = mon.game_player_id \
# 										INNER JOIN games_gameplayerrelation player \
# 										ON player.id <> opponent.id AND player.game_id = opponent.game_id \
# 										LEFT JOIN pokemon_pokemon details \
# 										ON details.id = mon.pokemon_id \
# 										LEFT JOIN pokemon_pokemontyperelation relation \
# 										ON relation.pokemon_id = details.id \
# 										LEFT JOIN pokemon_type type \
# 										ON type.id = relation.pokemon_type_id \
# 										WHERE player.id IN %s \
# 										AND player.personal_include = true \
# 										GROUP BY type.id',[tuple(game_list)])

# 	context = {
# 		'winrate':winrate,
# 		'response':response,
# 		'games':game_list,
# 		'game_ids':game_ids,
# 		'team':team_objects,
# 		'moves':moves,
# 		'individual':individual_usage,
# 		'opponents':opponents,
# 		'opponents_for_team':opponents_for_team,
# 		'types':opponent_types,
# 		'game_list':player_objects,
# 		'request':response,
# 		'included':included_game_ids
# 	}

# 			# if game not in included_games:
# 			# 	game.personal_include = False
# 			# 	game.save()

# 	# Make a post request to get include checkboxes mark true/false to personal include accordingly
# 	# if request.POST:
# 	# 	inclusions = request.POST.getlist('include_game')
# 	# 	context['inclusions'] = inclusions

# 	return render(request,"users/team_breakdown.html",context)
