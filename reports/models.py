from django.db import models

# Create your models here.
class Report(models.Model):
	title = models.CharField(max_length=1000)
	tier = models.ForeignKey(
		'tiers.Tier',
		on_delete=models.PROTECT,
		related_name='reports_of_tier')