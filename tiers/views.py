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
	ranked_bool = True

	games_in_tier = Game.objects.filter(tier=tier).count()

	pokemon_winrates = IndividualWinrate.objects.filter(Q(tier=tier)&Q(appearance_rate__gte=5)&Q(ranked=ranked_bool)).order_by('-winrate_used')
	lead_winrates = TeammateWinrate.objects.filter(Q(tier=tier)&Q(appearance_rate_lead__gte=0.1)&Q(ranked=ranked_bool)).order_by('-appearance_rate_lead')
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
		'gens':generation_list
	}

	return render(request,'formats_base.html',context)

def format_pokemon_view(request,generation,tier_name,pokemon_unique_name):
	tier = Tier.objects.get(generation=generation,tier_name=tier_name)
	pokemon = Pokemon.objects.filter(pokemon_unique_name=pokemon_unique_name).annotate(count=Count('game_where_pokemon_used',filter=Q(game_where_pokemon_used__game_player__game__tier=tier))).first()

	ranked_bool = True

	common_pokemon = Pokemon.objects.filter(Q(individual_winrates_of_pokemon__tier=tier)&Q(individual_winrates_of_pokemon__appearance_rate__gte=5)&Q(individual_winrates_of_pokemon__ranked=ranked_bool)).order_by('pokemon_display_name')
	teammates = TeammateWinrate.objects.filter(Q(pokemon=pokemon)&Q(tier=tier)&(Q(pairing_frequency__gte=5)|Q(game_count__gte=500))&Q(ranked=ranked_bool)).order_by('-winrate')
	opponents = OpponentWinrate.objects.filter(Q(pokemon=pokemon)&Q(tier=tier)&Q(opponent__in=common_pokemon)&Q(ranked=ranked_bool)).order_by('-winrate')
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