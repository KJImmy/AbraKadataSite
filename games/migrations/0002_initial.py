# Generated by Django 4.1.3 on 2023-05-26 17:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('games', '0001_initial'),
        ('tiers', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0001_initial'),
        ('pokemon', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pokemonusage',
            name='user_pokemon',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='user_pokemon', to='users.pokemononteam'),
        ),
        migrations.AddField(
            model_name='player',
            name='site_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='username_of_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='moveusage',
            name='move',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='pokemon_that_used_move', to='pokemon.move'),
        ),
        migrations.AddField(
            model_name='moveusage',
            name='pokemon',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='moves_used_by_pokemon', to='games.pokemonusage'),
        ),
        migrations.AddField(
            model_name='gameplayerrelation',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='players_in_game', to='games.game'),
        ),
        migrations.AddField(
            model_name='gameplayerrelation',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='games_of_player', to='games.player'),
        ),
        migrations.AddField(
            model_name='gameplayerrelation',
            name='team',
            field=models.ManyToManyField(related_name='player_team', through='games.PokemonUsage', to='pokemon.pokemon'),
        ),
        migrations.AddField(
            model_name='gameplayerrelation',
            name='user_team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='user_team', to='users.userteam'),
        ),
        migrations.AddField(
            model_name='game',
            name='players',
            field=models.ManyToManyField(related_name='game_players', through='games.GamePlayerRelation', to='games.player'),
        ),
        migrations.AddField(
            model_name='game',
            name='tier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='games_of_format', to='tiers.tier'),
        ),
        migrations.AlterUniqueTogether(
            name='moveusage',
            unique_together={('pokemon', 'move')},
        ),
        migrations.AlterUniqueTogether(
            name='gameplayerrelation',
            unique_together={('game', 'player')},
        ),
    ]