# Generated by Django 4.1.4 on 2023-04-18 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tiers', '0007_teamorcore_player_teamorcore_pokemon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tier',
            name='style',
            field=models.CharField(choices=[('VGC', 'Videogame Championship'), ('SS', 'Smogon Singles'), ('SD', 'Smogon Doubles'), ('U', 'Uncategorized')], default='U', max_length=3),
        ),
        migrations.AlterField(
            model_name='tier',
            name='valid',
            field=models.BooleanField(default=False),
        ),
    ]