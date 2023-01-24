from django.shortcuts import render
from django.db.models import Count,When,Case,Q,F,PositiveIntegerField,FloatField,ExpressionWrapper
from django.contrib.staticfiles import finders

from .models import Tier,IndividualWinrate,TeammateWinrate,OpponentWinrate,MoveWinrate,TeraWinrate
from games.models import PokemonUsage,Game,GamePlayerRelation
from pokemon.models import Pokemon,Move,Type

from decimal import Decimal
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
	tier_list = Tier.objects.all().order_by('style')
	generation_list = Tier.objects.distinct('generation').order_by('-generation')
	tier = Tier.objects.get(generation=generation,tier_name=tier_name)

	games_in_tier = Game.objects.filter(tier=tier).count()

	# pokemon_winrates = Pokemon.objects.filter(game_where_pokemon_used__game_player__game__tier=tier). \
	# 		annotate(game_count=Count('game_where_pokemon_used')). \
	# 		annotate(game_wins=Count('pk',filter=Q(game_where_pokemon_used__game_player__winner=True))). \
	# 		annotate(winrate=ExpressionWrapper(F('game_wins') * Decimal('100.0') / F('game_count'),FloatField())). \
	# 		annotate(appearance_rate=ExpressionWrapper(F('game_count') * Decimal('100.0') / teams_in_tier,FloatField())). \
	# 		filter(appearance_rate__gte=5). \
	# 		order_by('-winrate')

	pokemon_winrates = IndividualWinrate.objects.filter(Q(tier=tier)&Q(appearance_rate__gte=5)).order_by('-winrate')
	lead_winrates = TeammateWinrate.objects.filter(Q(tier=tier)&Q(appearance_rate_lead__gte=0.1)).order_by('-appearance_rate_lead')
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
	# lead_winrates = TeammateWinrate.objects.filter(Q(tier=tier)&Q(appearance_rate_lead__gte=1)).exclude(pk__in=exclude_pks).order_by('-winrate_lead')

	context = {
		'tier':tier,
		'winrates':pokemon_winrates,
		'leads':new_lead_queryset,
		'tiers':tier_list,
		'gens':generation_list
	}

	return render(request,'formats_base.html',context)

def format_pokemon_view(request,generation,tier_name,pokemon_unique_name):
	tier = Tier.objects.get(generation=generation,tier_name=tier_name)
	pokemon = Pokemon.objects.get(pokemon_unique_name=pokemon_unique_name)

	# games_with_pokemon = Game.objects.filter(players_in_game__pokemon_of_player__pokemon=pokemon). \
	# 	filter(tier=tier)
	# players_with_pokemon = GamePlayerRelation.objects.filter(pokemon_of_player__pokemon=pokemon). \
	# 	filter(game__tier=tier)
	# players_against_pokemon = GamePlayerRelation.objects.filter(game__in=games_with_pokemon). \
	# 	filter(game__tier=tier). \
	# 	exclude(id__in=players_with_pokemon)
	# # games_with_tera_pokemon_count = Game.objects.filter(Q(players_in_game=players_with_pokemon)&~Q(game_where_pokemon_used__tera_type=None))
	# # games_with_tera_pokemon_count = Game.objects.filter(Q(players_in_game__pokemon_of_player__pokemon=pokemon)&Q(tier=tier)&~Q(players_in_game__pokemon_of_player__tera_type=None)).count()


	# common_pokemon = Pokemon.objects.filter(game_where_pokemon_used__game_player__game__tier=tier). \
	# 		annotate(game_count=Count('game_where_pokemon_used')). \
	# 		annotate(appearance_rate=ExpressionWrapper(F('game_count') * Decimal('100.0') / teams_in_tier,FloatField())). \
	# 		filter(appearance_rate__gte=5). \
	# 		order_by('pokemon_display_name')


	# individual = Pokemon.objects.filter(pokemon_unique_name=pokemon_unique_name).values(). \
	# 	annotate(game_count=Count('pk',filter=Q(game_where_pokemon_used__game_player__in=players_with_pokemon))). \
	# 	annotate(game_wins=Count('pk',filter=Q(game_where_pokemon_used__game_player__in=players_with_pokemon)&Q(game_where_pokemon_used__game_player__winner=True))). \
	# 	annotate(winrate=ExpressionWrapper(F('game_wins') * Decimal('100.0') / F('game_count'),FloatField())). \
	# 	annotate(appearance_rate=ExpressionWrapper(F('game_count') * Decimal('100.0') / teams_in_tier,FloatField())). \
	# 	annotate(used_count=Count('pk',filter=Q(game_where_pokemon_used__game_player__in=players_with_pokemon)&Q(game_where_pokemon_used__used=True))). \
	# 	annotate(used_wins=Count('pk',filter=Q(game_where_pokemon_used__game_player__in=players_with_pokemon)&Q(game_where_pokemon_used__game_player__winner=True)&Q(game_where_pokemon_used__used=True))). \
	# 	annotate(used_winrate=ExpressionWrapper(F('used_wins') * Decimal('100.0') / F('used_count'),FloatField())). \
	# 	annotate(lead_count=Count('pk',filter=Q(game_where_pokemon_used__game_player__in=players_with_pokemon)&Q(game_where_pokemon_used__lead=True))). \
	# 	annotate(lead_wins=Count('pk',filter=Q(game_where_pokemon_used__game_player__in=players_with_pokemon)&Q(game_where_pokemon_used__game_player__winner=True)&Q(game_where_pokemon_used__lead=True))). \
	# 	annotate(lead_winrate=ExpressionWrapper(F('lead_wins') * Decimal('100.0') / F('lead_count'),FloatField())). \
	# 	annotate(tera_games=Count('pk',filter=Q(game_where_pokemon_used__game_player__in=players_with_pokemon)&~Q(game_where_pokemon_used__tera_type=None))). \
	# 	annotate(tera_frequency=ExpressionWrapper(F('tera_games') * Decimal('100.0') / F('game_count'),FloatField())). \
	# 	first()

	# # common_pokemon = Pokemon.objects.filter(game_where_pokemon_used__game_player__game__tier=tier). \
	# # 		values().annotate(game_count=Count('game_where_pokemon_used')). \
	# # 		annotate(appearance_rate=ExpressionWrapper(F('game_count') * Decimal('100.0') / teams_in_tier,FloatField())). \
	# # 		filter(appearance_rate__gte=5)

	# # to find games where display pokemon and teammate were used or lead together, make subquery for display pokemon and filter games of teammate used/lead that are in games of display pokemon used/lead
	# teammates = Pokemon.objects.filter(Q(game_where_pokemon_used__game_player__in=players_with_pokemon)). \
	# 	annotate(game_count=Count('pk',filter=Q(game_where_pokemon_used__game_player__in=players_with_pokemon))). \
	# 	filter(game_count__gte=100). \
	# 	annotate(game_wins=Count('pk',filter=Q(game_where_pokemon_used__game_player__in=players_with_pokemon)&Q(game_where_pokemon_used__game_player__winner=True))). \
	# 	annotate(winrate=ExpressionWrapper(F('game_wins') * Decimal('100.0') / F('game_count'),FloatField())). \
	# 	annotate(appearance_rate=ExpressionWrapper(F('game_count') * Decimal('100.0') / teams_in_tier,FloatField())). \
	# 	annotate(pairing_frequency=ExpressionWrapper(F('game_count') * Decimal('100.0') / individual['game_count'],FloatField())). \
	# 	filter(pairing_frequency__gte=5). \
	# 	order_by('-winrate')

	# # Determine whether to use all games where both mons in team preview or only games where both mons used
	# opponents = Pokemon.objects.filter(Q(game_where_pokemon_used__game_player__in=players_against_pokemon)). \
	# 	annotate(game_count=Count('pk',filter=Q(game_where_pokemon_used__game_player__in=players_against_pokemon))). \
	# 	filter(game_count__gte=100). \
	# 	annotate(game_wins=Count('pk',filter=Q(game_where_pokemon_used__game_player__in=players_against_pokemon)&Q(game_where_pokemon_used__game_player__winner=False))). \
	# 	annotate(winrate=ExpressionWrapper(F('game_wins') * Decimal('100.0') / F('game_count'),FloatField())). \
	# 	annotate(appearance_rate=ExpressionWrapper(F('game_count') * Decimal('100.0') / teams_in_tier,FloatField())). \
	# 	filter(id__in=common_pokemon). \
	# 	order_by('-winrate')

	# moves = Move.objects.filter(Q(pokemon_that_used_move__pokemon__pokemon=pokemon)&Q(pokemon_that_used_move__pokemon__game_player__game__tier=tier)). \
	# 	annotate(game_count=Count('pk',filter=Q(pokemon_that_used_move__pokemon__pokemon=pokemon))). \
	# 	filter(game_count__gte=100). \
	# 	annotate(game_wins=Count('pk',filter=Q(pokemon_that_used_move__pokemon__pokemon=pokemon)&Q(pokemon_that_used_move__pokemon__game_player__winner=True))). \
	# 	annotate(winrate=ExpressionWrapper(F('game_wins') * Decimal('100.0') / F('game_count'),FloatField())). \
	# 	annotate(move_frequency=ExpressionWrapper(F('game_count') * Decimal('100.0') / individual['used_count'],FloatField())). \
	# 	filter(move_frequency__gte=5). \
	# 	order_by('-winrate')

	# tera_types = Type.objects.filter(Q(tera_type_of_pokemon__pokemon=pokemon)&Q(tera_type_of_pokemon__game_player__game__tier=tier)). \
	# 	values().annotate(game_count=Count('pk',filter=Q(tera_type_of_pokemon__pokemon=pokemon))). \
	# 	annotate(game_wins=Count('pk',filter=Q(tera_type_of_pokemon__pokemon=pokemon)&Q(tera_type_of_pokemon__game_player__winner=True))). \
	# 	annotate(winrate=ExpressionWrapper(F('game_wins') * Decimal('100.0') / F('game_count'),FloatField())). \
	# 	filter(game_count__gte=100). \
	# 	annotate(tera_frequency=ExpressionWrapper(F('game_count') * Decimal('100.0') / individual['tera_games'],FloatField())). \
	# 	filter(tera_frequency__gte=5). \
	# 	order_by('-winrate')

	common_pokemon = Pokemon.objects.filter(Q(individual_winrates_of_pokemon__tier=tier)&Q(individual_winrates_of_pokemon__appearance_rate__gte=5)).order_by('pokemon_display_name')
	teammates = TeammateWinrate.objects.filter(Q(pokemon=pokemon)&Q(tier=tier)&Q(pairing_frequency__gte=5)).order_by('-winrate')
	opponents = OpponentWinrate.objects.filter(Q(pokemon=pokemon)&Q(tier=tier)&Q(opponent__in=common_pokemon)).order_by('-winrate')
	moves = MoveWinrate.objects.filter(Q(pokemon=pokemon)&Q(tier=tier)&Q(move_frequency__gte=5)).order_by('-winrate')
	tera_types = TeraWinrate.objects.filter(Q(pokemon=pokemon)&Q(tier=tier)&Q(type_frequency__gte=5)).order_by('-winrate')
	individual = IndividualWinrate.objects.get(Q(pokemon=pokemon)&Q(tier=tier))

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