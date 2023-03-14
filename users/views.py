import operator
import json

from django.shortcuts import render,redirect
from django.urls import reverse
from django.db import connection

from .forms import ShowdownUsernameForm,SubmitGameForm,CustomUserCreationForm
from .utils import validate_username
from games.utils import add_game_from_link
from games.models import Player,GamePlayerRelation,PokemonUsage,Game
from pokemon.models import Pokemon,Move
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.middleware import get_user

# Create your views here.
def dashboard_view(request):
	context = {}
	return render(request,"users/dashboard.html",context)

def stats_view(request):
	user = get_user(request)
	player = Player.objects.filter(site_user__isnull=False).filter(site_user=user.id)

	results = {}
	for p in player:
		# Go through all instances of player's games
		for t in p.games_of_player.all():

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

	# Calc winrates
	for tier in results.keys():
		for team in results[tier].keys():
			results[tier][team]["Winrate"] = round(results[tier][team]["Won"] * 100 / results[tier][team]["Played"],2)

	context = {
		'results':results
	}
	return render(request,"users/user_stats.html",context)

def breakdown_view(request):
	response = request.POST

	game_list = [int(s) for s in response['games'].replace('[','').replace(']','').split(',')]
	team_ids  =	[int(s) for s in response['team'].replace('[','').replace(']','').split(',')]

	game_objects = GamePlayerRelation.objects.filter(pk__in=game_list)
	team_objects = Pokemon.objects.filter(pk__in=team_ids)

	with connection.cursor() as cur:
		cur.execute('	SELECT ROUND(CAST(COUNT(*) FILTER (WHERE player.winner = true) AS DECIMAL) * 100 / CAST(COUNT(*) AS DECIMAL),2) AS winrate \
						FROM games_gameplayerrelation player \
						WHERE player.id IN %s',[tuple(game_list)])
		winrate = cur.fetchone()[0]
		winrate = float(winrate)

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
												GROUP BY mon.pokemon_id',[len(game_list),len(game_list),tuple(game_list)])

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
											GROUP BY mon_c.pokemon_id \
											) c ON c.pokemon_id = mon.pokemon_id \
								WHERE player.id IN %s \
								GROUP BY move_id,mon.pokemon_id,c.count',[tuple(game_list),tuple(game_list)])

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
										GROUP BY opp_mon.pokemon_id,mon.pokemon_id',[tuple(game_list)])

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
												GROUP BY mon.pokemon_id',[tuple(game_list)])

	context = {
		'winrate':winrate,
		'response':response,
		'games':game_list,
		'team':team_objects,
		'moves':moves,
		'individual':individual_usage,
		'opponents':opponents,
		'opponents_for_team':opponents_for_team
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

	if response and request.user.is_authenticated:
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