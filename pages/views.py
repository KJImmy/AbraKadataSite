import json

from django.shortcuts import render

from pokemon.models import Pokemon,PokemonTypeRelation
from tiers.models import Tier
# Create your views here.
def home_view(request):
	pokemon = Pokemon.objects.get(pokemon_unique_name='skeledirge')
	context = {
			'pokemon':pokemon
		}
	return render(request,'home.html',context)

def about_view(request):
	return render(request,'about.html',{})

def support_view(request):
	return render(request,'support.html',{})
