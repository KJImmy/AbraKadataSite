from django.core.management.base import BaseCommand, CommandError
from tiers.models import Tier
from games.models import PokemonUsage
from django.db.models import Count,When,Case,Q,F,PositiveIntegerField,FloatField,ExpressionWrapper
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder

import json
import operator
import itertools as i
import collections
import math
import random

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return i.chain.from_iterable(i.combinations(s, r) for r in range(len(s)+1))

class Command(BaseCommand):

	def handle(*args, **options):
		all_cores_dict = {}
		all_teams_dict = {}
		# tier_set = Tier.objects.all()
		tier_set = Tier.objects.filter(pk=14)

		for tier in tier_set:
			print(tier)
			used_pokemon = PokemonUsage.objects.filter(Q(game_player__game__tier=tier)&Q(game_player__game__ranked=True)).\
								prefetch_related('game_player').prefetch_related('pokemon')

			tier_teams = {}
			tier_cores = {}

			last_player = None
			cur_team 	= None

			for m in used_pokemon:
				cur_player = m.game_player

				if cur_player == last_player:
					cur_team.append(m.pokemon)

				else:
					if cur_team != None:
						cur_team.sort(key=operator.attrgetter('pk'))
						team_tuple = tuple(cur_team)

						if team_tuple not in tier_teams.keys():
							tier_teams.update({team_tuple:{	"Won":0,
															"Played":0,
															"Winrate":None,
															"Players":[],
															"UniquePlayers":[]}})
						tier_teams[team_tuple]["Played"] += 1

						if last_player.winner == True:
							tier_teams[team_tuple]["Won"] += 1

						tier_teams[team_tuple]["Players"].append(last_player)

						if last_player.player not in tier_teams[team_tuple]["UniquePlayers"]:
							tier_teams[team_tuple]["UniquePlayers"].append(last_player.player)

						all_cores_from_team = powerset(cur_team)

						for core in all_cores_from_team:
							if len(core) < 2 or len(core) > 4:
								continue
							if core not in tier_cores.keys():
								tier_cores.update({core:{	"Won":0,
															"Played":0,
															"Winrate":0,
															"Players":[],
															"UniquePlayers":[]}})

							tier_cores[core]["Played"] += 1

							if last_player.winner == True:
								tier_cores[core]["Won"] += 1

							tier_cores[core]["Players"].append(last_player)

							if last_player.player not in tier_cores[core]["UniquePlayers"]:
								tier_cores[core]["UniquePlayers"].append(last_player.player)


					last_player = cur_player
					cur_team 	= []
					cur_team.append(m.pokemon)

			for team in tier_teams.keys():
				tier_teams[team]["Winrate"] = round(tier_teams[team]["Won"]*100/tier_teams[team]["Played"],2)

			for core in tier_cores.keys():
				tier_cores[core]["Winrate"] = round(tier_cores[core]["Won"]*100/tier_cores[core]["Played"],2)

			all_teams_dict.update({tier.id:tier_teams})
			all_cores_dict.update({tier.id:tier_cores})

		all_dict = {"Teams":all_teams_dict,"Cores":all_cores_dict}

		with open("sample.json", "w") as outfile:
			json.dumps(all_dict, cls=DjangoJSONEncoder)