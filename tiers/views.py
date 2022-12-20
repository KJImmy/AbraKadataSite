from django.shortcuts import render
from django.db.models import Count,When,Case,Q,F,PositiveIntegerField,FloatField,ExpressionWrapper
from django.contrib.staticfiles import finders

from .models import Tier
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
	teams_in_tier = games_in_tier * 2

	pokemon_winrates = Pokemon.objects.filter(game_where_pokemon_used__game_player__game__tier=tier). \
			annotate(game_count=Count('game_where_pokemon_used')). \
			annotate(game_wins=Count('pk',filter=Q(game_where_pokemon_used__game_player__winner=True))). \
			annotate(winrate=ExpressionWrapper(F('game_wins') * Decimal('100.0') / F('game_count'),FloatField())). \
			annotate(appearance_rate=ExpressionWrapper(F('game_count') * Decimal('100.0') / teams_in_tier,FloatField())). \
			filter(appearance_rate__gte=5). \
			order_by('-winrate')

	context = {
		'tier':tier,
		'winrates':pokemon_winrates,
		'game_count':games_in_tier,
		'tiers':tier_list,
		'gens':generation_list
	}

	return render(request,'formats_base.html',context)

def format_pokemon_view(request,generation,tier_name,pokemon_unique_name):
	tier = Tier.objects.get(generation=generation,tier_name=tier_name)
	teams_in_tier = Game.objects.filter(tier=tier).count()
	teams_in_tier *= 2
	pokemon = Pokemon.objects.get(pokemon_unique_name=pokemon_unique_name)

	games_with_pokemon = Game.objects.filter(players_in_game__pokemon_of_player__pokemon=pokemon). \
		filter(tier=tier)
	players_with_pokemon = GamePlayerRelation.objects.filter(pokemon_of_player__pokemon=pokemon). \
		filter(game__tier=tier)
	players_against_pokemon = GamePlayerRelation.objects.filter(game__in=games_with_pokemon). \
		filter(game__tier=tier). \
		exclude(id__in=players_with_pokemon)
	# games_with_tera_pokemon_count = Game.objects.filter(Q(players_in_game=players_with_pokemon)&~Q(game_where_pokemon_used__tera_type=None))
	# games_with_tera_pokemon_count = Game.objects.filter(Q(players_in_game__pokemon_of_player__pokemon=pokemon)&Q(tier=tier)&~Q(players_in_game__pokemon_of_player__tera_type=None)).count()




	individual = Pokemon.objects.filter(pokemon_unique_name=pokemon_unique_name).values(). \
		annotate(game_count=Count('pk',filter=Q(game_where_pokemon_used__game_player__in=players_with_pokemon))). \
		annotate(game_wins=Count('pk',filter=Q(game_where_pokemon_used__game_player__in=players_with_pokemon)&Q(game_where_pokemon_used__game_player__winner=True))). \
		annotate(winrate=ExpressionWrapper(F('game_wins') * Decimal('100.0') / F('game_count'),FloatField())). \
		annotate(appearance_rate=ExpressionWrapper(F('game_count') * Decimal('100.0') / teams_in_tier,FloatField())). \
		annotate(used_count=Count('pk',filter=Q(game_where_pokemon_used__game_player__in=players_with_pokemon)&Q(game_where_pokemon_used__used=True))). \
		annotate(used_wins=Count('pk',filter=Q(game_where_pokemon_used__game_player__in=players_with_pokemon)&Q(game_where_pokemon_used__game_player__winner=True)&Q(game_where_pokemon_used__used=True))). \
		annotate(used_winrate=ExpressionWrapper(F('used_wins') * Decimal('100.0') / F('used_count'),FloatField())). \
		annotate(lead_count=Count('pk',filter=Q(game_where_pokemon_used__game_player__in=players_with_pokemon)&Q(game_where_pokemon_used__lead=True))). \
		annotate(lead_wins=Count('pk',filter=Q(game_where_pokemon_used__game_player__in=players_with_pokemon)&Q(game_where_pokemon_used__game_player__winner=True)&Q(game_where_pokemon_used__lead=True))). \
		annotate(lead_winrate=ExpressionWrapper(F('lead_wins') * Decimal('100.0') / F('lead_count'),FloatField())). \
		annotate(tera_games=Count('pk',filter=Q(game_where_pokemon_used__game_player__in=players_with_pokemon)&~Q(game_where_pokemon_used__tera_type=None))). \
		annotate(tera_frequency=ExpressionWrapper(F('tera_games') * Decimal('100.0') / F('game_count'),FloatField())). \
		first()

	# common_pokemon = Pokemon.objects.filter(game_where_pokemon_used__game_player__game__tier=tier). \
	# 		values().annotate(game_count=Count('game_where_pokemon_used')). \
	# 		annotate(appearance_rate=ExpressionWrapper(F('game_count') * Decimal('100.0') / teams_in_tier,FloatField())). \
	# 		filter(appearance_rate__gte=5)

	# to find games where display pokemon and teammate were used or lead together, make subquery for display pokemon and filter games of teammate used/lead that are in games of display pokemon used/lead
	teammates = Pokemon.objects.filter(Q(game_where_pokemon_used__game_player__in=players_with_pokemon)). \
		annotate(game_count=Count('pk',filter=Q(game_where_pokemon_used__game_player__in=players_with_pokemon))). \
		filter(game_count__gte=100). \
		annotate(game_wins=Count('pk',filter=Q(game_where_pokemon_used__game_player__in=players_with_pokemon)&Q(game_where_pokemon_used__game_player__winner=True))). \
		annotate(winrate=ExpressionWrapper(F('game_wins') * Decimal('100.0') / F('game_count'),FloatField())). \
		annotate(appearance_rate=ExpressionWrapper(F('game_count') * Decimal('100.0') / teams_in_tier,FloatField())). \
		annotate(pairing_frequency=ExpressionWrapper(F('game_count') * Decimal('100.0') / individual['game_count'],FloatField())). \
		order_by('-winrate')

	opponents = Pokemon.objects.filter(Q(game_where_pokemon_used__game_player__in=players_against_pokemon)). \
		annotate(game_count=Count('pk',filter=Q(game_where_pokemon_used__game_player__in=players_against_pokemon))). \
		filter(game_count__gte=100). \
		annotate(game_wins=Count('pk',filter=Q(game_where_pokemon_used__game_player__in=players_against_pokemon)&Q(game_where_pokemon_used__game_player__winner=False))). \
		annotate(winrate=ExpressionWrapper(F('game_wins') * Decimal('100.0') / F('game_count'),FloatField())). \
		annotate(appearance_rate=ExpressionWrapper(F('game_count') * Decimal('100.0') / teams_in_tier,FloatField())). \
		order_by('-winrate')

	moves = Move.objects.filter(Q(pokemon_that_used_move__pokemon__pokemon=pokemon)&Q(pokemon_that_used_move__pokemon__game_player__game__tier=tier)). \
		annotate(game_count=Count('pk',filter=Q(pokemon_that_used_move__pokemon__pokemon=pokemon))). \
		filter(game_count__gte=100). \
		annotate(game_wins=Count('pk',filter=Q(pokemon_that_used_move__pokemon__pokemon=pokemon)&Q(pokemon_that_used_move__pokemon__game_player__winner=True))). \
		annotate(winrate=ExpressionWrapper(F('game_wins') * Decimal('100.0') / F('game_count'),FloatField())). \
		annotate(move_frequency=ExpressionWrapper(F('game_count') * Decimal('100.0') / individual['used_count'],FloatField())). \
		order_by('-winrate')

	tera_types = Type.objects.filter(Q(tera_type_of_pokemon__pokemon=pokemon)&Q(tera_type_of_pokemon__game_player__game__tier=tier)). \
		values().annotate(game_count=Count('pk',filter=Q(tera_type_of_pokemon__pokemon=pokemon))). \
		annotate(game_wins=Count('pk',filter=Q(tera_type_of_pokemon__pokemon=pokemon)&Q(tera_type_of_pokemon__game_player__winner=True))). \
		annotate(winrate=ExpressionWrapper(F('game_wins') * Decimal('100.0') / F('game_count'),FloatField())). \
		filter(game_count__gte=100). \
		annotate(tera_frequency=ExpressionWrapper(F('game_count') * Decimal('100.0') / individual['tera_games'],FloatField())). \
		order_by('-winrate')

	common_pokemon = Pokemon.objects.filter(game_where_pokemon_used__game_player__game__tier=tier). \
			annotate(game_count=Count('game_where_pokemon_used')). \
			annotate(appearance_rate=ExpressionWrapper(F('game_count') * Decimal('100.0') / teams_in_tier,FloatField())). \
			filter(appearance_rate__gte=5). \
			order_by('pokemon_display_name')

	context = {
		'tier':tier,
		'pokemon':pokemon,
		'teammates':teammates,
		'opponents':opponents,
		'moves':moves,
		'individual':individual,
		'tera_types':tera_types,
		'common_pokemon':common_pokemon
		# 'search_list':search_list
		# 'search_reference':search_reference
	}
	return render(request,'formats_pokemon.html',context)