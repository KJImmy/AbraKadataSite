# Generated by Django 4.1.3 on 2022-12-04 20:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pokemon', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('link', models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='PokemonUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='games.game')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='player2', to='games.player')),
                ('pokemon', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='pokemon.pokemon')),
            ],
        ),
        migrations.CreateModel(
            name='MoveUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('move', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='pokemon.move')),
                ('pokemon', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='games.pokemonusage')),
            ],
        ),
        migrations.CreateModel(
            name='GamePlayerRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pre_rating', models.PositiveIntegerField()),
                ('post_rating', models.PositiveIntegerField()),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='games.game')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='games.player')),
            ],
        ),
        migrations.AddField(
            model_name='game',
            name='winner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='player1', to='games.player'),
        ),
    ]
