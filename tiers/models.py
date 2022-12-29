from django.db import models

# Create your models here.
class Tier(models.Model):
	tier_name = models.CharField(max_length=100)
	tier_display_name = models.CharField(max_length=100)
	generation = models.PositiveIntegerField()
	style = models.CharField(
		max_length=3,
		choices=[('VGC','Videogame Championship'),('SS','Smogon Singles'),('SD','Smogon Doubles')])
	has_megas = models.BooleanField(default=False)
	has_zmoves = models.BooleanField(default=False)
	has_dynamax = models.BooleanField(default=False)
	has_tera = models.BooleanField(default=False)

class IndividualWinrates(models.Model):
	pokemon = models.ForeignKey(
		'pokemon.Pokemon',
		on_delete=models.PROTECT,
		related_name='pokemon4')

class TeammateWinrates(models.Model):
	pokemon = models.ForeignKey(
		'pokemon.Pokemon',
		on_delete=models.PROTECT,
		related_name='pokemon5')
	teammate = models.ForeignKey(
		'pokemon.Pokemon',
		on_delete=models.PROTECT,
		related_name='pokemon6')

class OpponentWinrates(models.Model):
	pokemon = models.ForeignKey(
		'pokemon.Pokemon',
		on_delete=models.PROTECT,
		related_name='pokemon7')
	opponent = models.ForeignKey(
		'pokemon.Pokemon',
		on_delete=models.PROTECT,
		related_name='pokemon8')

class MoveWinrates(models.Model):
	pokemon = models.ForeignKey(
		'pokemon.Pokemon',
		on_delete=models.PROTECT,
		related_name='pokemon9')
	move = models.ForeignKey(
		'pokemon.Move',
		on_delete=models.PROTECT)

class SpeedTier(models.Model):
	pokemon = models.ForeignKey(
		'pokemon.Pokemon',
		on_delete=models.PROTECT,
		related_name='speed_tier_of_pokemon')
	tier = models.ForeignKey(
		'Tier',
		on_delete=models.PROTECT,
		related_name='speed_tiers_of_tier')
	speed = models.PositiveIntegerField()
	speed_stage = models.IntegerField()