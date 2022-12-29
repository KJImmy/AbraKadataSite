from django.contrib import admin

from .models import Pokemon,Move,Item,Ability,Type,PokemonTypeRelation,PokemonAbilityRelation,Learnset
# Register your models here.
admin.site.register(Pokemon)
admin.site.register(Move)
admin.site.register(Item)
admin.site.register(Ability)
admin.site.register(Type)
admin.site.register(PokemonAbilityRelation)
admin.site.register(PokemonTypeRelation)
admin.site.register(Learnset)