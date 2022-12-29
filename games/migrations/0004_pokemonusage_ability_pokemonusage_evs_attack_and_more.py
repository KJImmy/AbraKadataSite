# Generated by Django 4.1.3 on 2022-12-05 15:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pokemon', '0005_alter_move_move_unique_name'),
        ('games', '0003_alter_gameplayerrelation_player_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pokemonusage',
            name='ability',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ability_for_used_pokemon', to='pokemon.ability'),
        ),
        migrations.AddField(
            model_name='pokemonusage',
            name='evs_attack',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='pokemonusage',
            name='evs_defense',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='pokemonusage',
            name='evs_hp',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='pokemonusage',
            name='evs_special_attack',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='pokemonusage',
            name='evs_special_defense',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='pokemonusage',
            name='evs_speed',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='pokemonusage',
            name='item',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='item_for_used_pokemon', to='pokemon.item'),
        ),
        migrations.AddField(
            model_name='pokemonusage',
            name='lead',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='pokemonusage',
            name='nature',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='pokemonusage',
            name='used',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='gameplayerrelation',
            name='post_rating',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='gameplayerrelation',
            name='pre_rating',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='pokemonusage',
            name='game_player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='pokemon_of_player', to='games.gameplayerrelation'),
        ),
        migrations.AlterUniqueTogether(
            name='gameplayerrelation',
            unique_together={('game', 'player')},
        ),
        migrations.AlterUniqueTogether(
            name='moveusage',
            unique_together={('pokemon', 'move')},
        ),
    ]
