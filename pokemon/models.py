from django.db import models

# Create your models here.
class Move(models.Model):
	move_unique_name = models.CharField(max_length=100,unique=True)
	move_display_name = models.CharField(max_length=100)
	move_type = models.ForeignKey(
		'Type',
		on_delete=models.PROTECT,
		related_name='move_type')
	damage_class = models.CharField(max_length=100)
	base_power = models.PositiveIntegerField(null=True)
	accuracy = models.PositiveIntegerField(null=True)
	pp = models.PositiveIntegerField(null=True)
	priority = models.IntegerField(null=True)
	targets = models.PositiveIntegerField(null=True)
	effect_chance = models.PositiveIntegerField(null=True)

class Item(models.Model):
	item_unique_name = models.CharField(max_length=100)
	item_display_name = models.CharField(max_length=100)

class Ability(models.Model):
	ability_unique_name = models.CharField(max_length=100,unique=True)
	ability_display_name = models.CharField(max_length=100)

class Type(models.Model):
	type_name = models.CharField(max_length=100,unique=True)
	type_color = models.CharField(max_length=10,null=True)
	damage_class = models.CharField(max_length=100,null=True)

class Pokemon(models.Model):
	pokemon_unique_name = models.CharField(max_length=100,unique=True)
	pokemon_display_name = models.CharField(max_length=100)
	dex_number = models.PositiveIntegerField()
	img_number = models.PositiveIntegerField()
	stats_hp = models.PositiveIntegerField()
	stats_attack = models.PositiveIntegerField()
	stats_defense = models.PositiveIntegerField()
	stats_special_attack = models.PositiveIntegerField()
	stats_special_defense = models.PositiveIntegerField()
	stats_speed = models.PositiveIntegerField()
	stats_total = models.PositiveIntegerField()
	pokemon_types = models.ManyToManyField(Type,related_name='pokemon_typing',through='PokemonTypeRelation')
	pokemon_abilities = models.ManyToManyField(Ability,through='PokemonAbilityRelation')
	learnset = models.ManyToManyField(Move,through='Learnset')

class PokemonTypeRelation(models.Model):
	pokemon = models.ForeignKey('Pokemon',on_delete=models.PROTECT,related_name='types_of_pokemon')
	pokemon_type = models.ForeignKey('Type',on_delete=models.PROTECT,related_name='pokemon_of_type',null=True)
	slot = models.PositiveIntegerField()

	class Meta:
		unique_together = ['pokemon','pokemon_type']

class PokemonAbilityRelation(models.Model):
	pokemon = models.ForeignKey('Pokemon',on_delete=models.PROTECT,related_name='ability_pokemon')
	ability = models.ForeignKey('Ability',on_delete=models.PROTECT,related_name='pokemon_ability')
	hidden = models.BooleanField()

	class Meta:
		unique_together = ['pokemon','ability']

class Learnset(models.Model):
	pokemon = models.ForeignKey('Pokemon',on_delete=models.PROTECT,related_name='move_pokemon')
	move = models.ForeignKey('Move',on_delete=models.PROTECT,related_name='pokemon_move')
	generation = models.PositiveIntegerField()
	learn_method = models.CharField(max_length=100,null=True)

	class Meta:
		unique_together = ['pokemon','move','generation']