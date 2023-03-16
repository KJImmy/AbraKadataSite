from django.shortcuts import render
from django.db.models import Count,When,Case,Q,F,PositiveIntegerField,FloatField,ExpressionWrapper,Prefetch,Value,Exists,OuterRef
from django.contrib.staticfiles import finders

from .models import Tier,IndividualWinrate,TeammateWinrate,OpponentWinrate,MoveWinrate,TeraWinrate,TeamOrCore
from .forms import FilterForm
from games.models import PokemonUsage,Game,GamePlayerRelation
from pokemon.models import Pokemon,Move,Type

from decimal import Decimal
import datetime

# Create your views here.
def formats_view(request):
	tier_list = Tier.objects.all().order_by('style')
	generation_list = Tier.objects.distinct('generation').order_by('-generation')
	context = {
		'tiers':tier_list,
		'gens':generation_list
	}
	return render(request,'formats.html',context)

def format_base_view(request,generation,tier_name):
	stats_filter = request.GET

	tier_list = Tier.objects.all().order_by('-generation','style')
	generation_list = tier_list.values('generation').distinct('generation')
	tier = tier_list.get(generation=generation,tier_name=tier_name)
	ranked_bool = True

	# pokemon_winrates = tier.individual_winrates_of_tier.filter(Q(appearance_rate__gte=5)&Q(ranked=ranked_bool)).order_by('-winrate_used')
	# lead_winrates = tier.teammate_winrates_of_tier.filter(Q(ranked=ranked_bool)&Q(appearance_rate_lead__gte=0.1)).order_by('-appearance_rate_lead')

	pokemon_winrates = IndividualWinrate.objects.filter(Q(tier=tier)&Q(appearance_rate__gte=5)&Q(ranked=ranked_bool)).order_by('-winrate_used')	

	lead_winrates = TeammateWinrate.objects.filter(Q(tier=tier)&Q(appearance_rate_lead__gte=0.1)&Q(ranked=ranked_bool)).\
						order_by('-appearance_rate_lead').select_related('pokemon')
	lead_pairs = []
	exclude_pks = []
	new_lead_set = []
	for l in lead_winrates.iterator():
		pair_list = []
		pair_list.append(l.pokemon.pokemon_display_name)
		pair_list.append(l.teammate.pokemon_display_name)
		pair_list.sort()
		if pair_list not in lead_pairs:
			lead_pairs.append(pair_list)
			new_lead_set.append(l)
		else:
			exclude_pks.append(l.id)
	new_lead_queryset = new_lead_set[:10]

	context = {
		'tier':tier,
		'winrates':pokemon_winrates,
		'leads':new_lead_queryset,
		'tiers':tier_list,
		'gens':generation_list,
		'filtered':False,
		'form':FilterForm
	}

	if stats_filter:
		begin = '2010-01-01 00:00:00'
		end = datetime.datetime.now()
		min_rating = 1000
		max_rating = 10000

		response_begin = stats_filter['start_date_year'] + " " + stats_filter['start_date_month'] + " " + stats_filter['start_date_day']
		response_end = stats_filter['end_date_year'] + " " + stats_filter['end_date_month'] + " " + stats_filter['end_date_day']
		response_min_rating = stats_filter['minimum_rating']
		response_max_rating = stats_filter['maximum_rating']

		if response_begin != '  ':
			begin = response_begin + ' 00:00:00'
		if response_end != '  ':
			end = response_end + ' 00:00:00'
		if response_min_rating != '':
			min_rating = response_min_rating
		if response_max_rating != '':
			max_rating = response_max_rating

		filtered_winrates_query = '	SELECT \
										pokemon_id AS id,\
										game.tier_id,\
										ROUND(CAST(COUNT(pokemon_id) AS DECIMAL) * 100 / CAST(c.count AS DECIMAL),2) AS appearance_rate,\
										ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE mon.used = true) AS DECIMAL) * 100 / CAST(COUNT(pokemon_id) AS DECIMAL),2) AS used_rate,\
										ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE mon.lead = true) AS DECIMAL) * 100 / CAST(COUNT(pokemon_id) AS DECIMAL),2) AS lead_rate,\
										ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE player.winner = true AND pokemon_id NOT IN (\
											SELECT pokemon_id \
											FROM games_pokemonusage mon_sw1 \
											LEFT JOIN games_gameplayerrelation player_sw1 \
											ON player_sw1.id = mon_sw1.game_player_id \
											WHERE player_sw1.game_id = player.game_id \
											AND player_sw1.id <> player.id \
											)) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(pokemon_id) FILTER (WHERE pokemon_id NOT IN ( \
											SELECT pokemon_id \
											FROM games_pokemonusage mon_sw2 \
											LEFT JOIN games_gameplayerrelation player_sw2 \
											ON player_sw2.id = mon_sw2.game_player_id \
											WHERE player_sw2.game_id = player.game_id \
											AND player_sw2.id <> player.id \
											)) AS DECIMAL),0),2) AS winrate,\
										ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE mon.used = true AND player.winner = true AND pokemon_id NOT IN (\
											SELECT pokemon_id \
											FROM games_pokemonusage mon_su1 \
											LEFT JOIN games_gameplayerrelation player_su1 \
											ON player_su1.id = mon_su1.game_player_id \
											WHERE player_su1.game_id = player.game_id \
											AND player_su1.id <> player.id \
											AND mon_su1.used = true \
											)) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(pokemon_id) FILTER (WHERE mon.used = true AND pokemon_id NOT IN ( \
											SELECT pokemon_id \
											FROM games_pokemonusage mon_su2 \
											LEFT JOIN games_gameplayerrelation player_su2 \
											ON player_su2.id = mon_su2.game_player_id \
											WHERE player_su2.game_id = player.game_id \
											AND player_su2.id <> player.id \
											AND mon_su2.used = true \
											)) AS DECIMAL),0),2) AS winrate_used,\
										ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE mon.lead = true AND player.winner = true AND pokemon_id NOT IN ( \
											SELECT pokemon_id \
											FROM games_pokemonusage mon_sl1 \
											LEFT JOIN games_gameplayerrelation player_sl1 \
											ON player_sl1.id = mon_sl1.game_player_id \
											WHERE player_sl1.game_id = player.game_id \
											AND player_sl1.id <> player.id \
											AND mon_sl1.used = lead \
											)) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(pokemon_id) FILTER (WHERE mon.lead = true AND pokemon_id NOT IN ( \
											SELECT pokemon_id \
											FROM games_pokemonusage mon_sl2 \
											LEFT JOIN games_gameplayerrelation player_sl2 \
											ON player_sl2.id = mon_sl2.game_player_id \
											WHERE player_sl2.game_id = player.game_id \
											AND player_sl2.id <> player.id \
											AND mon_sl2.used = lead \
											)) AS DECIMAL),0),2) AS winrate_lead, \
										ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE mon.dynamaxed = true) AS DECIMAL) * 100 / CAST(COUNT(pokemon_id) AS DECIMAL),2) AS dynamax_frequency, \
										ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE mon.dynamaxed = true AND player.winner = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(pokemon_id) FILTER (WHERE mon.dynamaxed = true) AS DECIMAL),0),2) AS dynamax_winrate, \
										ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE mon.tera_type_id IS NOT NULL) AS DECIMAL) * 100 / CAST(COUNT(pokemon_id) AS DECIMAL),2) AS tera_frequency \
									FROM games_pokemonusage mon \
									LEFT JOIN games_gameplayerrelation player \
									ON mon.game_player_id = player.id \
									LEFT JOIN games_game game \
									ON game.id = player.game_id \
									LEFT JOIN pokemon_pokemon poke \
									ON mon.pokemon_id = poke.id \
									LEFT JOIN ( \
										SELECT game1.tier_id, COUNT(player1.id) \
										FROM games_gameplayerrelation player1 \
										LEFT JOIN games_game game1 \
										ON game1.id = player1.game_id \
										WHERE game1.start_time >= %s \
										AND game1.start_time <= %s \
										AND game1.rating >= %s \
										AND game1.rating <= %s \
										GROUP BY game1.tier_id \
									) c ON c.tier_id = game.tier_id \
									WHERE game.tier_id = %s \
									AND start_time >= %s \
									AND start_time <= %s \
									AND game.rating >= %s \
									AND game.rating <= %s \
									GROUP BY pokemon_id,game.tier_id,c.count \
									HAVING ROUND(CAST(COUNT(pokemon_id) AS DECIMAL) * 100 / CAST(c.count AS DECIMAL),2) > 5 \
									ORDER BY appearance_rate DESC'

		query_input = [begin,end,min_rating,max_rating,tier.id,begin,end,min_rating,max_rating]

		filtered_winrates = Pokemon.objects.raw(filtered_winrates_query,query_input)
		context['winrates'] = filtered_winrates
		context['filtered'] = True
		context['response'] = stats_filter

	return render(request,'formats_base.html',context)

def format_base_view_test(request,generation,tier_name):
	stats_filter = request.GET

	tier_list = Tier.objects.all().order_by('-generation','style')
	generation_list = tier_list.values('generation').distinct('generation')
	tier = tier_list.get(generation=generation,tier_name=tier_name)
	ranked_bool = True

	# pokemon_winrates = tier.individual_winrates_of_tier.filter(Q(appearance_rate__gte=5)&Q(ranked=ranked_bool)).order_by('-winrate_used')
	# lead_winrates = tier.teammate_winrates_of_tier.filter(Q(ranked=ranked_bool)&Q(appearance_rate_lead__gte=0.1)).order_by('-appearance_rate_lead')

	pokemon_winrates = IndividualWinrate.objects.filter(Q(tier=tier)&Q(appearance_rate__gte=5)&Q(ranked=ranked_bool)).order_by('-winrate_used')	

	lead_winrates = TeammateWinrate.objects.filter(Q(tier=tier)&Q(appearance_rate_lead__gte=0.1)&Q(ranked=ranked_bool)).\
						order_by('-appearance_rate_lead').select_related('pokemon')
	lead_pairs = []
	exclude_pks = []
	new_lead_set = []
	for l in lead_winrates.iterator():
		pair_list = []
		pair_list.append(l.pokemon.pokemon_display_name)
		pair_list.append(l.teammate.pokemon_display_name)
		pair_list.sort()
		if pair_list not in lead_pairs:
			lead_pairs.append(pair_list)
			new_lead_set.append(l)
		else:
			exclude_pks.append(l.id)
	new_lead_queryset = new_lead_set[:10]

	context = {
		'tier':tier,
		'winrates':pokemon_winrates,
		'leads':new_lead_queryset,
		'tiers':tier_list,
		'gens':generation_list,
		'filtered':False,
		'form':FilterForm
	}

	if stats_filter:
		begin = '2010-01-01 00:00:00'
		end = datetime.datetime.now()
		min_rating = 1000
		max_rating = 10000

		response_begin = stats_filter['start_date_year'] + " " + stats_filter['start_date_month'] + " " + stats_filter['start_date_day']
		response_end = stats_filter['end_date_year'] + " " + stats_filter['end_date_month'] + " " + stats_filter['end_date_day']
		response_min_rating = stats_filter['minimum_rating']
		response_max_rating = stats_filter['maximum_rating']

		if response_begin != '  ':
			begin = response_begin + ' 00:00:00'
		if response_end != '  ':
			end = response_end + ' 00:00:00'
		if response_min_rating != '':
			min_rating = response_min_rating
		if response_max_rating != '':
			max_rating = response_max_rating

		filtered_winrates_query = '	SELECT \
										pokemon_id AS id,\
										game.tier_id,\
										ROUND(CAST(COUNT(pokemon_id) AS DECIMAL) * 100 / CAST(c.count AS DECIMAL),2) AS appearance_rate,\
										ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE mon.used = true) AS DECIMAL) * 100 / CAST(COUNT(pokemon_id) AS DECIMAL),2) AS used_rate,\
										ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE mon.lead = true) AS DECIMAL) * 100 / CAST(COUNT(pokemon_id) AS DECIMAL),2) AS lead_rate,\
										ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE player.winner = true AND pokemon_id NOT IN (\
											SELECT pokemon_id \
											FROM games_pokemonusage mon_sw1 \
											LEFT JOIN games_gameplayerrelation player_sw1 \
											ON player_sw1.id = mon_sw1.game_player_id \
											WHERE player_sw1.game_id = player.game_id \
											AND player_sw1.id <> player.id \
											)) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(pokemon_id) FILTER (WHERE pokemon_id NOT IN ( \
											SELECT pokemon_id \
											FROM games_pokemonusage mon_sw2 \
											LEFT JOIN games_gameplayerrelation player_sw2 \
											ON player_sw2.id = mon_sw2.game_player_id \
											WHERE player_sw2.game_id = player.game_id \
											AND player_sw2.id <> player.id \
											)) AS DECIMAL),0),2) AS winrate,\
										ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE mon.used = true AND player.winner = true AND pokemon_id NOT IN (\
											SELECT pokemon_id \
											FROM games_pokemonusage mon_su1 \
											LEFT JOIN games_gameplayerrelation player_su1 \
											ON player_su1.id = mon_su1.game_player_id \
											WHERE player_su1.game_id = player.game_id \
											AND player_su1.id <> player.id \
											AND mon_su1.used = true \
											)) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(pokemon_id) FILTER (WHERE mon.used = true AND pokemon_id NOT IN ( \
											SELECT pokemon_id \
											FROM games_pokemonusage mon_su2 \
											LEFT JOIN games_gameplayerrelation player_su2 \
											ON player_su2.id = mon_su2.game_player_id \
											WHERE player_su2.game_id = player.game_id \
											AND player_su2.id <> player.id \
											AND mon_su2.used = true \
											)) AS DECIMAL),0),2) AS winrate_used,\
										ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE mon.lead = true AND player.winner = true AND pokemon_id NOT IN ( \
											SELECT pokemon_id \
											FROM games_pokemonusage mon_sl1 \
											LEFT JOIN games_gameplayerrelation player_sl1 \
											ON player_sl1.id = mon_sl1.game_player_id \
											WHERE player_sl1.game_id = player.game_id \
											AND player_sl1.id <> player.id \
											AND mon_sl1.used = lead \
											)) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(pokemon_id) FILTER (WHERE mon.lead = true AND pokemon_id NOT IN ( \
											SELECT pokemon_id \
											FROM games_pokemonusage mon_sl2 \
											LEFT JOIN games_gameplayerrelation player_sl2 \
											ON player_sl2.id = mon_sl2.game_player_id \
											WHERE player_sl2.game_id = player.game_id \
											AND player_sl2.id <> player.id \
											AND mon_sl2.used = lead \
											)) AS DECIMAL),0),2) AS winrate_lead, \
										ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE mon.dynamaxed = true) AS DECIMAL) * 100 / CAST(COUNT(pokemon_id) AS DECIMAL),2) AS dynamax_frequency, \
										ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE mon.dynamaxed = true AND player.winner = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(pokemon_id) FILTER (WHERE mon.dynamaxed = true) AS DECIMAL),0),2) AS dynamax_winrate, \
										ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE mon.tera_type_id IS NOT NULL) AS DECIMAL) * 100 / CAST(COUNT(pokemon_id) AS DECIMAL),2) AS tera_frequency \
									FROM games_pokemonusage mon \
									LEFT JOIN games_gameplayerrelation player \
									ON mon.game_player_id = player.id \
									LEFT JOIN games_game game \
									ON game.id = player.game_id \
									LEFT JOIN pokemon_pokemon poke \
									ON mon.pokemon_id = poke.id \
									LEFT JOIN ( \
										SELECT game1.tier_id, COUNT(player1.id) \
										FROM games_gameplayerrelation player1 \
										LEFT JOIN games_game game1 \
										ON game1.id = player1.game_id \
										WHERE game1.start_time >= %s \
										AND game1.start_time <= %s \
										AND game1.rating >= %s \
										AND game1.rating <= %s \
										GROUP BY game1.tier_id \
									) c ON c.tier_id = game.tier_id \
									WHERE game.tier_id = %s \
									AND start_time >= %s \
									AND start_time <= %s \
									AND game.rating >= %s \
									AND game.rating <= %s \
									GROUP BY pokemon_id,game.tier_id,c.count \
									HAVING ROUND(CAST(COUNT(pokemon_id) AS DECIMAL) * 100 / CAST(c.count AS DECIMAL),2) > 5 \
									ORDER BY appearance_rate DESC'

		query_input = [begin,end,min_rating,max_rating,tier.id,begin,end,min_rating,max_rating]

		filtered_winrates = Pokemon.objects.raw(filtered_winrates_query,query_input)
		context['winrates'] = filtered_winrates
		context['filtered'] = True
		context['response'] = stats_filter

	return render(request,'filter_test.html',context)

def format_pokemon_view(request,generation,tier_name,pokemon_unique_name):
	tier = Tier.objects.get(generation=generation,tier_name=tier_name)
	pokemon = Pokemon.objects.filter(pokemon_unique_name=pokemon_unique_name).annotate(count=Count('game_where_pokemon_used',filter=Q(game_where_pokemon_used__game_player__game__tier=tier))).first()

	ranked_bool = True

	common_pokemon = Pokemon.objects.filter(Q(individual_winrates_of_pokemon__tier=tier)&Q(individual_winrates_of_pokemon__appearance_rate__gte=5)&Q(individual_winrates_of_pokemon__ranked=ranked_bool)).order_by('pokemon_display_name')
	teammates = TeammateWinrate.objects.filter(Q(pokemon=pokemon)&Q(tier=tier)&(Q(pairing_frequency__gte=5)|Q(game_count__gte=500))&Q(ranked=ranked_bool)).order_by('-winrate')
	opponents = OpponentWinrate.objects.filter(Q(pokemon=pokemon)&Q(tier=tier)&Q(opponent__in=common_pokemon)&Q(ranked=ranked_bool)).order_by('-winrate_used')
	moves = MoveWinrate.objects.filter(Q(pokemon=pokemon)&Q(tier=tier)&(Q(move_frequency__gte=5)|Q(game_count__gte=100))&Q(ranked=ranked_bool)).order_by('-winrate')
	tera_types = TeraWinrate.objects.filter(Q(pokemon=pokemon)&Q(tier=tier)&(Q(type_frequency__gte=5)|Q(game_count__gte=100))&Q(ranked=ranked_bool)).order_by('-winrate')
	individual = IndividualWinrate.objects.get(Q(pokemon=pokemon)&Q(tier=tier)&Q(ranked=ranked_bool))

	# Add player_count and max_times_used_by_player to guard against people messing with the stats

	context = {
		'tier':tier,
		'pokemon':pokemon,
		'teammates':teammates,
		'opponents':opponents,
		'moves':moves,
		'individual':individual,
		'tera_types':tera_types,
		'common_pokemon':common_pokemon
	}
	return render(request,'formats_pokemon.html',context)

def format_teams_view(request,generation,tier_name):
	tier = Tier.objects.get(generation=generation,tier_name=tier_name)

	tcs = tier.teams_and_cores_of_tier.annotate(mon_count=Count('pokemon_of_team_or_core'))
	full_teams = tcs.filter(Q(mon_count=6)&Q(game_count__gte=100))\
					.annotate(winrate=ExpressionWrapper(F('wins') * Decimal('100.0') / F('game_count'),FloatField()))\
					.filter(game_count__gte=100)\
					.order_by('-game_count')

	context = {
		'teams':full_teams
	}

	return render(request,'format_teams.html',context)

def format_team_breakdown_view(request,generation,tier_name,team_id):
	raw_query = Pokemon.objects.raw('SELECT pokemon_id AS id,\
										ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE mon.used = true) AS DECIMAL) * 100 / CAST(COUNT(pokemon_id) AS DECIMAL),2) AS used_rate,\
										ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE mon.lead = true) AS DECIMAL) * 100 / CAST(COUNT(pokemon_id) AS DECIMAL),2) AS lead_rate,\
										ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE player.winner = true) AS DECIMAL) * 100 / CAST(COUNT(pokemon_id) AS DECIMAL),2) AS winrate,\
										ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE mon.used = true AND player.winner = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(pokemon_id) FILTER (WHERE mon.used = true) AS DECIMAL),0),2) AS winrate_used,\
										ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE mon.lead = true AND player.winner = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(pokemon_id) FILTER (WHERE mon.lead = true) AS DECIMAL),0),2) AS winrate_lead,\
										ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE mon.dynamaxed = true) AS DECIMAL) * 100 / CAST(COUNT(pokemon_id) AS DECIMAL),2) AS dynamax_frequency,\
										ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE mon.dynamaxed = true AND player.winner = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(pokemon_id) FILTER (WHERE mon.dynamaxed = true) AS DECIMAL),0),2) AS dynamax_winrate,\
										ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE mon.tera_type_id IS NOT NULL) AS DECIMAL) * 100 / CAST(COUNT(pokemon_id) AS DECIMAL),2) AS tera_frequency \
									FROM games_pokemonusage mon \
									LEFT JOIN games_gameplayerrelation player ON mon.game_player_id = player.id \
									LEFT JOIN games_game game ON game.id = player.game_id \
									LEFT JOIN pokemon_pokemon poke ON poke.id = mon.pokemon_id \
									LEFT JOIN tiers_playerwithteamorcore team ON team.player_id = player.id \
									WHERE team.team_or_core_id = %s \
									GROUP BY pokemon_id \
									ORDER BY id',[team_id])

	matchups = TeamOrCore.objects.raw('SELECT team.id AS used_team,opponent_team.id AS id,COUNT(*) \
										FROM tiers_teamorcore team \
										LEFT JOIN tiers_playerwithteamorcore player_link ON team.id = player_link.team_or_core_id \
										LEFT JOIN games_gameplayerrelation player ON player.id = player_link.player_id \
										LEFT JOIN games_gameplayerrelation opponent ON player.game_id = opponent.game_id AND opponent.id <> player.id \
										LEFT JOIN tiers_playerwithteamorcore opponent_link ON opponent_link.player_id = opponent.id \
										LEFT JOIN tiers_teamorcore opponent_team ON opponent_link.team_or_core_id = opponent_team.id \
										WHERE team.id = %s \
										GROUP BY team.id,opponent_team.id \
										HAVING COUNT(*) > 10 \
										ORDER BY count DESC',[team_id])

	# Find how the whole team does against other pokemon (and cores?)
	# Find out how each individual pokemon on the team does against other pokemon

	context = {
		'raw':raw_query,
		'matchups':matchups
	}

	return render(request,'format_team_breakdown.html',context)


def format_cores_view(request,generation,tier_name):
	tier = Tier.objects.get(generation=generation,tier_name=tier_name)

	tcs = tier.teams_and_cores_of_tier.annotate(mon_count=Count('pokemon_of_team_or_core'))
	cores = tcs.filter(Q(mon_count__lt=6)&Q(game_count__gte=100))\
					.annotate(winrate=ExpressionWrapper(F('wins') * Decimal('100.0') / F('game_count'),FloatField()))\
					.filter(game_count__gte=800)\
					.order_by('-game_count')

	context = {
		'cores':cores
	}

	return render(request,'format_cores.html',context)

def format_core_breakdown_view(request,generation,tier_name,core_id):
	common_pokemon = Pokemon.objects.filter(Q(individual_winrates_of_pokemon__tier__generation=generation)\
											&Q(individual_winrates_of_pokemon__tier__tier_name=tier_name)\
											&Q(individual_winrates_of_pokemon__appearance_rate__gte=5)\
											&Q(individual_winrates_of_pokemon__ranked=True))\
											.order_by('pokemon_display_name').values_list('id',flat=True)

	raw_query = Pokemon.objects.raw('	SELECT pokemon_id AS id,\
											ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE mon.used = true) AS DECIMAL) * 100 / CAST(COUNT(pokemon_id) AS DECIMAL),2) AS used_rate,\
											ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE mon.lead = true) AS DECIMAL) * 100 / CAST(COUNT(pokemon_id) AS DECIMAL),2) AS lead_rate,\
											ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE player.winner = true) AS DECIMAL) * 100 / CAST(COUNT(pokemon_id) AS DECIMAL),2) AS winrate,\
											ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE mon.used = true AND player.winner = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(pokemon_id) FILTER (WHERE mon.used = true) AS DECIMAL),0),2) AS winrate_used,\
											ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE mon.lead = true AND player.winner = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(pokemon_id) FILTER (WHERE mon.lead = true) AS DECIMAL),0),2) AS winrate_lead,\
											ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE mon.dynamaxed = true) AS DECIMAL) * 100 / CAST(COUNT(pokemon_id) AS DECIMAL),2) AS dynamax_frequency,\
											ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE mon.dynamaxed = true AND player.winner = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(pokemon_id) FILTER (WHERE mon.dynamaxed = true) AS DECIMAL),0),2) AS dynamax_winrate,\
											ROUND(CAST(COUNT(pokemon_id) FILTER (WHERE mon.tera_type_id IS NOT NULL) AS DECIMAL) * 100 / CAST(COUNT(pokemon_id) AS DECIMAL),2) AS tera_frequency \
										FROM games_pokemonusage mon \
										LEFT JOIN games_gameplayerrelation player ON mon.game_player_id = player.id \
										LEFT JOIN games_game game ON game.id = player.game_id \
										LEFT JOIN pokemon_pokemon poke ON poke.id = mon.pokemon_id \
										LEFT JOIN tiers_playerwithteamorcore team ON team.player_id = player.id \
										WHERE team.team_or_core_id = %s \
										AND pokemon_id IN (	SELECT pokemon_id \
															FROM tiers_pokemononteamorcore \
															WHERE team_or_core_id = %s) \
										GROUP BY pokemon_id \
										ORDER BY id',[core_id,core_id])

	matchups = TeamOrCore.objects.raw('	SELECT team.id AS used_team,opponent_team.id AS id,COUNT(*), \
											ROUND(CAST(COUNT(*) FILTER (WHERE player.winner = true) AS DECIMAL) * 100 / CAST(COUNT(*) AS DECIMAL),2) AS winrate\
										FROM tiers_teamorcore team \
										LEFT JOIN tiers_playerwithteamorcore player_link ON team.id = player_link.team_or_core_id \
										LEFT JOIN games_gameplayerrelation player ON player.id = player_link.player_id \
										LEFT JOIN games_gameplayerrelation opponent ON player.game_id = opponent.game_id AND opponent.id <> player.id \
										LEFT JOIN tiers_playerwithteamorcore opponent_link ON opponent_link.player_id = opponent.id \
										LEFT JOIN tiers_teamorcore opponent_team ON opponent_link.team_or_core_id = opponent_team.id \
										WHERE team.id = %s \
										GROUP BY team.id,opponent_team.id \
										HAVING COUNT(*) > 500 \
										ORDER BY count DESC',[core_id])

	moves = Move.objects.raw('	SELECT move_id AS id,mon.pokemon_id,\
									ROUND(CAST(COUNT(*) FILTER (WHERE player.winner = true) AS DECIMAL) * 100 / CAST(COUNT(*) AS DECIMAL),2) AS winrate,\
									ROUND(CAST(COUNT(*) AS DECIMAL) * 100 / CAST(c.count AS DECIMAL),2) AS move_frequency \
								FROM games_pokemonusage mon \
								LEFT JOIN games_moveusage move ON move.pokemon_id = mon.id \
								LEFT JOIN games_gameplayerrelation player ON player.id = mon.game_player_id \
								LEFT JOIN tiers_playerwithteamorcore team ON player.id = team.player_id \
								LEFT JOIN (	SELECT mon_c.pokemon_id,COUNT(*) FILTER (WHERE mon_c.used = true) \
											FROM games_pokemonusage mon_c \
											LEFT JOIN games_gameplayerrelation player_c ON player_c.id = mon_c.game_player_id \
											LEFT JOIN tiers_playerwithteamorcore team_c ON team_c.player_id = player_c.id \
											WHERE team_c.team_or_core_id = %s \
											GROUP BY mon_c.pokemon_id \
								) c ON c.pokemon_id = mon.pokemon_id \
								WHERE team.team_or_core_id = %s \
								AND mon.pokemon_id IN (	SELECT pokemon_id \
														FROM tiers_pokemononteamorcore  \
														WHERE team_or_core_id = %s) \
								AND move_id IS NOT NULL \
								GROUP BY move_id,mon.pokemon_id,c.count \
								HAVING ROUND(CAST(COUNT(*) AS DECIMAL) * 100 / CAST(c.count AS DECIMAL),2) > 5 \
								ORDER BY mon.pokemon_id',[core_id,core_id,core_id])

	opponents = Pokemon.objects.raw('	SELECT mon2.pokemon_id AS id, mon1.pokemon_id AS cur_mon, \
											ROUND(CAST(COUNT(mon1.pokemon_id) FILTER (WHERE player1.winner = true) AS DECIMAL) * 100 / CAST(COUNT(mon2.pokemon_id) AS DECIMAL),2) AS winrate,\
											ROUND(CAST(COUNT(mon1.pokemon_id) FILTER (WHERE player1.winner = true AND mon1.used = true AND mon2.used = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(mon1.pokemon_id) FILTER (WHERE mon1.used = true AND mon2.used = true) AS DECIMAL),0),2) AS winrate_used,\
											ROUND(CAST(COUNT(mon1.pokemon_id) FILTER (WHERE player1.winner = true AND mon1.lead = true AND mon2.lead = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(mon1.pokemon_id) FILTER (WHERE mon1.lead = true AND mon2.lead = true) AS DECIMAL),0),2) AS winrate_lead,\
											ROUND(CAST(COUNT(mon1.pokemon_id) FILTER (WHERE mon1.used = true AND mon2.used = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(mon1.pokemon_id) AS DECIMAL),0),2) AS faceoff_frequency,\
											ROUND(CAST(COUNT(mon1.pokemon_id) FILTER (WHERE mon1.lead = true AND mon2.lead = true) AS DECIMAL) * 100 / NULLIF(CAST(COUNT(mon1.pokemon_id) AS DECIMAL),0),2) AS faceoff_frequency_lead \
										FROM games_pokemonusage mon1 \
										LEFT JOIN games_gameplayerrelation player1 \
										ON mon1.game_player_id = player1.id \
										LEFT JOIN games_gameplayerrelation player2 \
										ON player1.game_id = player2.game_id AND player1.id <> player2.id \
										LEFT JOIN games_pokemonusage mon2 \
										ON player2.id = mon2.game_player_id \
										LEFT JOIN tiers_playerwithteamorcore core1 \
										ON core1.player_id = player1.id \
										WHERE core1.team_or_core_id = %s \
										AND mon1.pokemon_id IN (SELECT pokemon_id \
																FROM tiers_pokemononteamorcore \
																WHERE team_or_core_id = %s) \
										AND mon2.pokemon_id IN %s \
										GROUP BY mon2.pokemon_id,mon1.pokemon_id \
										ORDER BY mon2.pokemon_id',[core_id,core_id,tuple(common_pokemon)])

	teammates = Pokemon.objects.raw('	SELECT mon1.pokemon_id AS id, \
											ROUND(CAST(COUNT(mon1.pokemon_id) FILTER (WHERE player.winner = true) AS DECIMAL) * 100 / CAST(COUNT(mon1.pokemon_id) AS DECIMAL),2) AS winrate,\
											ROUND(CAST(COUNT(mon1.pokemon_id) AS DECIMAL) * 100 / CAST(core2.game_count AS DECIMAL),2) AS pairing_frequency \
										FROM games_pokemonusage mon1 \
										LEFT JOIN games_gameplayerrelation player \
										ON player.id = mon1.game_player_id \
										LEFT JOIN tiers_playerwithteamorcore core \
										ON core.player_id = player.id \
										LEFT JOIN tiers_teamorcore core2 \
										ON core.team_or_core_id = core2.id \
										WHERE core.team_or_core_id = %s \
										AND mon1.pokemon_id NOT IN (SELECT pokemon_id \
																FROM tiers_pokemononteamorcore \
																WHERE team_or_core_id = %s) \
										GROUP BY mon1.pokemon_id,core2.game_count \
										HAVING ROUND(CAST(COUNT(mon1.pokemon_id) AS DECIMAL) * 100 / CAST(core2.game_count AS DECIMAL),2) > 5 \
										OR COUNT(*) > 1000 \
										ORDER BY mon1.pokemon_id',[core_id,core_id])

	# make sure I'm not including mons already in the core

	# Find how the whole team does against other pokemon (and cores?)
	# Find out how each individual pokemon on the team does against other pokemon

	context = {
		'raw':raw_query,
		'matchups':matchups,
		'moves':moves,
		'opponents':opponents,
		'teammates':teammates
	}

	return render(request,'format_core_breakdown.html',context)