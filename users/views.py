import operator

from django.shortcuts import render

from .forms import ShowdownUsernameForm,SubmitGameForm
from .utils import validate_username
from games.utils import add_game_from_link
from games.models import Player,GamePlayerRelation,PokemonUsage
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
			for p in cur_team:
				team.append(p.pokemon)
			team.sort(key=operator.attrgetter('pk'))
			tt = tuple(team)
			if tt not in results[cur_tier].keys():
				results[cur_tier].update({tt:{"Won":0,"Played":0,"Winrate":None,"GameList":[]}})
			results[cur_tier][tt]["GameList"].append(t)
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
	context = {}
	return render(request,"users/user_stats.html",context)

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