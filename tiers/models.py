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
	valid = models.BooleanField(default=True)

class IndividualWinrate(models.Model):
	pokemon = models.ForeignKey(
		'pokemon.Pokemon',
		on_delete=models.PROTECT,
		related_name='individual_winrates_of_pokemon')
	tier = models.ForeignKey(
		'Tier',
		on_delete=models.PROTECT,
		related_name='individual_winrates_of_tier')
	appearance_rate = models.DecimalField(max_digits=5,decimal_places=2)
	used_rate = models.DecimalField(max_digits=5,decimal_places=2)
	lead_rate = models.DecimalField(max_digits=5,decimal_places=2)
	winrate = models.DecimalField(max_digits=5,decimal_places=2,null=True)
	winrate_used = models.DecimalField(max_digits=5,decimal_places=2,null=True)
	winrate_lead = models.DecimalField(max_digits=5,decimal_places=2,null=True)
	dynamax_frequency = models.DecimalField(max_digits=5,decimal_places=2,null=True)
	dynamax_winrate = models.DecimalField(max_digits=5,decimal_places=2,null=True)
	tera_frequency = models.DecimalField(max_digits=5,decimal_places=2,null=True)
	ranked = models.BooleanField(default=False)

class TeammateWinrate(models.Model):
	pokemon = models.ForeignKey(
		'pokemon.Pokemon',
		on_delete=models.PROTECT,
		related_name='teammate_winrates_of_pokemon')
	teammate = models.ForeignKey(
		'pokemon.Pokemon',
		on_delete=models.PROTECT,
		related_name='pokemon6')
	tier = models.ForeignKey(
		'Tier',
		on_delete=models.PROTECT,
		related_name='teammate_winrates_of_tier')
	appearance_rate = models.DecimalField(max_digits=5,decimal_places=2)
	appearance_rate_lead = models.DecimalField(max_digits=5,decimal_places=2)
	used_rate = models.DecimalField(max_digits=5,decimal_places=2)
	lead_rate = models.DecimalField(max_digits=5,decimal_places=2)
	winrate = models.DecimalField(max_digits=5,decimal_places=2)
	winrate_used = models.DecimalField(max_digits=5,decimal_places=2,null=True)
	winrate_lead = models.DecimalField(max_digits=5,decimal_places=2,null=True)
	pairing_frequency = models.DecimalField(max_digits=5,decimal_places=2)
	ranked = models.BooleanField(default=False)

class OpponentWinrate(models.Model):
	pokemon = models.ForeignKey(
		'pokemon.Pokemon',
		on_delete=models.PROTECT,
		related_name='pokemon7')
	opponent = models.ForeignKey(
		'pokemon.Pokemon',
		on_delete=models.PROTECT,
		related_name='pokemon8')
	tier = models.ForeignKey(
		'Tier',
		on_delete=models.PROTECT,
		related_name='opponent_winrates_of_tier')
	winrate = models.DecimalField(max_digits=5,decimal_places=2)
	winrate_used = models.DecimalField(max_digits=5,decimal_places=2,null=True)
	winrate_lead = models.DecimalField(max_digits=5,decimal_places=2,null=True)
	faceoff_frequency = models.DecimalField(max_digits=5,decimal_places=2,null=True)
	faceoff_frequency_lead = models.DecimalField(max_digits=5,decimal_places=2,null=True)
	ranked = models.BooleanField(default=False)


class MoveWinrate(models.Model):
	pokemon = models.ForeignKey(
		'pokemon.Pokemon',
		on_delete=models.PROTECT,
		related_name='pokemon9')
	move = models.ForeignKey(
		'pokemon.Move',
		on_delete=models.PROTECT)
	tier = models.ForeignKey(
		'Tier',
		on_delete=models.PROTECT,
		related_name='move_winrates_of_tier')
	winrate = models.DecimalField(max_digits=5,decimal_places=2)
	move_frequency = models.DecimalField(max_digits=5,decimal_places=2)
	average_percent_damage = models.DecimalField(max_digits=5,decimal_places=2,null=True)
	ranked = models.BooleanField(default=False)

class TeraWinrate(models.Model):
	pokemon = models.ForeignKey(
		'pokemon.Pokemon',
		on_delete=models.PROTECT,
		related_name='aggregate_tera_type_of_pokemon')
	tera_type = models.ForeignKey(
		'pokemon.Type',
		on_delete=models.PROTECT,
		related_name='aggregate_pokemon_of_tera_type')
	tier = models.ForeignKey(
		'Tier',
		on_delete=models.PROTECT,
		related_name='tera_winrates_of_tier')
	winrate = models.DecimalField(max_digits=5,decimal_places=2)
	type_frequency = models.DecimalField(max_digits=5,decimal_places=2)
	ranked = models.BooleanField(default=False)

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