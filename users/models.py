from django.conf import settings
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from games.models import Player
# Create your models here.
class UserPSUsernameRelation(models.Model):
	site_user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.PROTECT,
		related_name='ps_names_of_user')
	ps_username = models.ForeignKey(
		'games.Player',
		on_delete=models.PROTECT,
		related_name='users_with_ps_name')
	include = models.BooleanField(default=True)

class UserTeam(models.Model):
	name = models.CharField(max_length=100,default="untitled")
	site_user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.PROTECT,
		related_name='team_of_user',
		null=True)
	username = models.ForeignKey(
		'games.Player',
		on_delete=models.PROTECT,
		related_name='team_of_ps_username',
		null=True)
	show = models.BooleanField(default=True)
	tier = models.ForeignKey(
		'tiers.Tier',
		on_delete=models.PROTECT,
		related_name='user_teams_of_tier',
		null=True)

class PokemonOnTeam(models.Model):
	team = models.ForeignKey(
		'UserTeam',
		on_delete=models.PROTECT,
		related_name='pokemon_on_user_team')
	pokemon = models.ForeignKey(
		'pokemon.Pokemon',
		on_delete=models.PROTECT,
		related_name='user_team_of_pokemon')
	level = models.PositiveIntegerField(default=100,validators=[MaxValueValidator(100),MinValueValidator(1)])
	ev_hp = models.PositiveIntegerField(default=0,validators=[MaxValueValidator(252)])
	ev_atk = models.PositiveIntegerField(default=0,validators=[MaxValueValidator(252)])
	ev_def = models.PositiveIntegerField(default=0,validators=[MaxValueValidator(252)])
	ev_spa = models.PositiveIntegerField(default=0,validators=[MaxValueValidator(252)])
	ev_spd = models.PositiveIntegerField(default=0,validators=[MaxValueValidator(252)])
	ev_spe = models.PositiveIntegerField(default=0,validators=[MaxValueValidator(252)])
	iv_hp = models.PositiveIntegerField(default=31,validators=[MaxValueValidator(31)])
	iv_atk = models.PositiveIntegerField(default=31,validators=[MaxValueValidator(31)])
	iv_def = models.PositiveIntegerField(default=31,validators=[MaxValueValidator(31)])
	iv_spa = models.PositiveIntegerField(default=31,validators=[MaxValueValidator(31)])
	iv_spd = models.PositiveIntegerField(default=31,validators=[MaxValueValidator(31)])
	iv_spe = models.PositiveIntegerField(default=31,validators=[MaxValueValidator(31)])
	ability = models.ForeignKey(
		'pokemon.Ability',
		on_delete=models.PROTECT,
		related_name='user_pokemon_with_ability',
		null=True)
	tera_type = models.ForeignKey(
		'pokemon.Type',
		on_delete=models.PROTECT,
		related_name='user_pokemon_with_tera_type',
		null=True)
	gigantamax = models.BooleanField(default=False)
	shiny = models.BooleanField(default=False)

	MALE="M"
	FEMALE="F"
	GENDERLESS="X"
	RANDOM="R"
	GENDER_CHOICES = [
		(MALE,"Male"),
		(FEMALE,"Female"),
		(GENDERLESS,"Genderless"),
		(RANDOM,"Random")
	]
	gender = models.CharField(
		max_length=1,
		choices = GENDER_CHOICES,
		default = RANDOM)

	nature = models.CharField(max_length=100,null=True)
	item = models.CharField(max_length=100,null=True)

class MoveOfPokemonOnTeam(models.Model):
	move = models.ForeignKey(
		'pokemon.Move',
		on_delete=models.PROTECT,
		related_name='user_pokemon_with_move')
	pokemon = models.ForeignKey(
		'PokemonOnTeam',
		on_delete=models.PROTECT,
		related_name='move_of_user_pokemon')