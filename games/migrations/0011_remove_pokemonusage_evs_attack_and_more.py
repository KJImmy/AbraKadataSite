# Generated by Django 4.1.3 on 2023-05-05 18:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_remove_pokemononteam_pokemon_and_more'),
        ('games', '0010_gameplayerrelation_personal_include'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pokemonusage',
            name='evs_attack',
        ),
        migrations.RemoveField(
            model_name='pokemonusage',
            name='evs_defense',
        ),
        migrations.RemoveField(
            model_name='pokemonusage',
            name='evs_hp',
        ),
        migrations.RemoveField(
            model_name='pokemonusage',
            name='evs_special_attack',
        ),
        migrations.RemoveField(
            model_name='pokemonusage',
            name='evs_special_defense',
        ),
        migrations.RemoveField(
            model_name='pokemonusage',
            name='evs_speed',
        ),
        migrations.RemoveField(
            model_name='pokemonusage',
            name='nature',
        ),
        migrations.AddField(
            model_name='moveusage',
            name='used',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='pokemonusage',
            name='user_pokemon',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='game_of_user_pokemon', to='users.pokemononteam'),
        ),
    ]
