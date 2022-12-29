# Generated by Django 4.1.3 on 2022-12-04 20:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ability_unique_name', models.CharField(max_length=100, unique=True)),
                ('ability_display_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_unique_name', models.CharField(max_length=100)),
                ('item_display_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Learnset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('generation', models.PositiveIntegerField()),
                ('learn_method', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Move',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('move_unique_name', models.CharField(max_length=100)),
                ('move_display_name', models.CharField(max_length=100)),
                ('base_power', models.PositiveIntegerField(null=True)),
                ('accuracy', models.PositiveIntegerField(null=True)),
                ('pp', models.PositiveIntegerField(null=True)),
                ('priority', models.IntegerField(null=True)),
                ('targets', models.PositiveIntegerField(null=True)),
                ('effect_chance', models.PositiveIntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Pokemon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pokemon_unique_name', models.CharField(max_length=100, unique=True)),
                ('pokemon_display_name', models.CharField(max_length=100)),
                ('dex_number', models.PositiveIntegerField()),
                ('img_number', models.PositiveIntegerField()),
                ('stats_hp', models.PositiveIntegerField()),
                ('stats_attack', models.PositiveIntegerField()),
                ('stats_defense', models.PositiveIntegerField()),
                ('stats_special_attack', models.PositiveIntegerField()),
                ('stats_special_defense', models.PositiveIntegerField()),
                ('stats_speed', models.PositiveIntegerField()),
                ('stats_total', models.PositiveIntegerField()),
                ('learnset', models.ManyToManyField(through='pokemon.Learnset', to='pokemon.move')),
            ],
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_name', models.CharField(max_length=100, unique=True)),
                ('type_color', models.CharField(max_length=10, null=True)),
                ('damage_class', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PokemonTypeRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slot', models.PositiveIntegerField()),
                ('pokemon', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='pokemon_of_type', to='pokemon.pokemon')),
                ('pokemon_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='types_of_pokemon', to='pokemon.type')),
            ],
            options={
                'unique_together': {('pokemon', 'pokemon_type')},
            },
        ),
        migrations.CreateModel(
            name='PokemonAbilityRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hidden', models.BooleanField()),
                ('ability', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='pokemon_ability', to='pokemon.ability')),
                ('pokemon', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ability_pokemon', to='pokemon.pokemon')),
            ],
            options={
                'unique_together': {('pokemon', 'ability')},
            },
        ),
        migrations.AddField(
            model_name='pokemon',
            name='pokemon_abilities',
            field=models.ManyToManyField(through='pokemon.PokemonAbilityRelation', to='pokemon.ability'),
        ),
        migrations.AddField(
            model_name='pokemon',
            name='pokemon_types',
            field=models.ManyToManyField(related_name='pokemon_typing', through='pokemon.PokemonTypeRelation', to='pokemon.type'),
        ),
        migrations.AddField(
            model_name='move',
            name='move_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='move_type', to='pokemon.type'),
        ),
        migrations.AddField(
            model_name='learnset',
            name='move',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='pokemon_move', to='pokemon.move'),
        ),
        migrations.AddField(
            model_name='learnset',
            name='pokemon',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='move_pokemon', to='pokemon.pokemon'),
        ),
        migrations.AlterUniqueTogether(
            name='learnset',
            unique_together={('pokemon', 'move', 'generation')},
        ),
    ]
