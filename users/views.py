import operator

from django.shortcuts import render

from games.models import Player,GamePlayerRelation,PokemonUsage

# Create your views here.
def dashboard_view(request):
	player = Player.objects.get(username='Sam360games')

	results = {}
	# Go through all instances of player's games
	for t in player.games_of_player.all():

		# Get formats in which games were played
		cur_tier = t.game.tier
		if cur_tier not in results.keys():
			results.update({cur_tier:{}})

		# Get team that was played
		cur_team = t.pokemon_of_player.all()
		team = []
		for p in cur_team:
			team.append(p.pokemon)
		team.sort(key=operator.attrgetter('pk'))
		tt = tuple(team)
		if tt not in results[cur_tier].keys():
			results[cur_tier].update({tt:{"Won":0,"Played":0,"Winrate":None,"Game List":[]}})
		results[cur_tier][tt]["Game List"].append(t)
		results[cur_tier][tt]["Played"] += 1
		if t.winner == True:
			results[cur_tier][tt]["Won"] += 1

	# Calc winrates
	for tier in results.keys():
		for team in results[tier].keys():
			results[tier][team]["Winrate"] = round(results[tier][team]["Won"] * 100 / results[tier][team]["Played"],2)


		# cur_team = t.pokemon_of_player.all()
		# team = []
		# for p in cur_team:
		# 	team.append(p.pokemon)
		# team.sort(key=operator.attrgetter('pk'))
		# tt = tuple(team)
		# if tt not in results.keys():
		# 	results.update({tt:{"won":0,"played":0}})
		# results[tt]["played"] += 1
		# if t.winner == True:
		# 	results[tt]["won"] += 1

	context = {
		'player':player,
		'results':results
	}
	return render(request,"users/dashboard.html",context)

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