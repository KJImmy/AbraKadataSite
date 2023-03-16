from django.conf import settings
from django.db import models

from pokemon.models import Pokemon,Move
# Create your models here.
class Player(models.Model):
	username = models.CharField(max_length=100,unique=True)
	site_user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.PROTECT,
		related_name='username_of_user',
		null=True)

class Game(models.Model):
	start_time = models.DateTimeField()
	link = models.CharField(max_length=1000,unique=True)
	players = models.ManyToManyField(Player,related_name='game_players',through='GamePlayerRelation')
	tier = models.ForeignKey(
		'tiers.Tier',
		related_name='games_of_format',
		on_delete=models.PROTECT)
	ranked = models.BooleanField(default=True)
	public = models.BooleanField(default=True)
	rating = models.PositiveIntegerField(null=True)

class PokemonUsage(models.Model):
	pokemon = models.ForeignKey(
		'pokemon.Pokemon',
		related_name='game_where_pokemon_used',
		on_delete=models.PROTECT)
	game_player = models.ForeignKey(
		'GamePlayerRelation',
		related_name='pokemon_of_player',
		on_delete=models.PROTECT)
	moveset = models.ManyToManyField(Move,related_name='pokemon_moveset',through='MoveUsage')
	used = models.BooleanField()
	lead = models.BooleanField()
	ability = models.ForeignKey(
		'pokemon.Ability',
		related_name='ability_for_used_pokemon',
		on_delete=models.PROTECT,
		null=True,
		default=None)
	item = models.ForeignKey(
		'pokemon.Item',
		related_name='item_for_used_pokemon',
		on_delete=models.PROTECT,
		null=True,
		default=None)
	evs_hp = models.PositiveIntegerField(default=None,null=True)
	evs_attack = models.PositiveIntegerField(default=None,null=True)
	evs_defense = models.PositiveIntegerField(default=None,null=True)
	evs_special_attack = models.PositiveIntegerField(default=None,null=True)
	evs_special_defense = models.PositiveIntegerField(default=None,null=True)
	evs_speed = models.PositiveIntegerField(default=None,null=True)
	nature = models.CharField(max_length=100,default=None,null=True)
	dynamaxed = models.BooleanField(null=True)
	tera_type = models.ForeignKey(
		'pokemon.Type',
		related_name='tera_type_of_pokemon',
		on_delete=models.PROTECT,
		null=True)

	# class Meta:
	# 	unique_together = ['pokemon','game_player']

class MoveUsage(models.Model):
	pokemon = models.ForeignKey(
		'PokemonUsage',
		related_name='moves_used_by_pokemon',
		on_delete=models.PROTECT)
	move = models.ForeignKey(
		'pokemon.Move',
		related_name='pokemon_that_used_move',
		on_delete=models.PROTECT)

	class Meta:
		unique_together = ['pokemon','move']

class GamePlayerRelation(models.Model):
	game = models.ForeignKey(
		'Game',
		related_name='players_in_game',
		on_delete=models.PROTECT)
	player = models.ForeignKey(
		'Player',
		related_name='games_of_player',
		on_delete=models.PROTECT)
	player_number = models.PositiveIntegerField()
	team = models.ManyToManyField(Pokemon,related_name='player_team',through='PokemonUsage')
	winner = models.BooleanField()
	rating_pre = models.PositiveIntegerField(null=True)
	rating_post = models.PositiveIntegerField(null=True)

	class Meta:
		unique_together = ['game','player']

class UserSubmittedGame(models.Model):
	game = models.ForeignKey(
		'Game',
		related_name='submitted_by',
		on_delete=models.PROTECT)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.PROTECT,
		related_name='games_submitted')