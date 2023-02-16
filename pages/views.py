from django.shortcuts import render
from django.db.models import Count,When,Case,Q,F,PositiveIntegerField,FloatField,ExpressionWrapper
from django.contrib.staticfiles import finders

from tiers.models import Tier,IndividualWinrate,TeammateWinrate,OpponentWinrate,MoveWinrate,TeraWinrate
from games.models import PokemonUsage,Game,GamePlayerRelation
from pokemon.models import Pokemon,Move

# Create your views here.
def home_view(request):
	top_14 = IndividualWinrate.objects.filter(Q(tier=14)&Q(appearance_rate__gte=5)&Q(ranked=True)).order_by('-winrate_used').first()
	top_3 = IndividualWinrate.objects.filter(Q(tier=3)&Q(appearance_rate__gte=5)&Q(ranked=True)).order_by('-winrate_used').first()

	vgc_tier = Tier.objects.get(id=14)
	singles_tier = Tier.objects.get(id=3)

	context = {
			'top_vgc':top_14,
			'vgc_tier':vgc_tier,
			'top_singles':top_3,
			'singles_tier':singles_tier,
			'home_page':True
		}

	return render(request,'home.html',context)

def about_view(request):
	return render(request,'about.html',{})

def support_view(request):
	return render(request,'support.html',{})

def reports_view(request):
	return render(request,'reports.html',{})
