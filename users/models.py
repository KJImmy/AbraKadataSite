from django.conf import settings
from django.db import models

# Create your models here.
class UserTeam(models.Model):
	site_user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.PROTECT,
		related_name='team_of_user')

class PokemonOnTeam(models.Model):
	team = models.ForeignKey(
		'UserTeam',
		on_delete=models.PROTECT,
		related_name='pokemon_on_user_team')
	pokemon = models.ForeignKey(
		'pokemon.Pokemon',
		on_delete=models.PROTECT,
		related_name='user_team_of_pokemon')
	level = models.PositiveIntegerField(default=100)
	ev_hp = models.PositiveIntegerField(default=0)
	ev_atk = models.PositiveIntegerField(default=0)
	ev_def = models.PositiveIntegerField(default=0)
	ev_spa = models.PositiveIntegerField(default=0)
	ev_spd = models.PositiveIntegerField(default=0)
	ev_spe = models.PositiveIntegerField(default=0)
	iv_hp = models.PositiveIntegerField(default=31)
	iv_atk = models.PositiveIntegerField(default=31)
	iv_def = models.PositiveIntegerField(default=31)
	iv_spa = models.PositiveIntegerField(default=31)
	iv_spd = models.PositiveIntegerField(default=31)
	iv_spe = models.PositiveIntegerField(default=31)
	move1 = models.ForeignKey(
		'pokemon.Move',
		on_delete=models.PROTECT,
		related_name='user_pokemon_with_move1',
		null=True)
	move2 = models.ForeignKey(
		'pokemon.Move',
		on_delete=models.PROTECT,
		related_name='user_pokemon_with_move2',
		null=True)
	move3 = models.ForeignKey(
		'pokemon.Move',
		on_delete=models.PROTECT,
		related_name='user_pokemon_with_move3',
		null=True)
	move4 = models.ForeignKey(
		'pokemon.Move',
		on_delete=models.PROTECT,
		related_name='user_pokemon_with_move4',
		null=True)
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
