# Generated by Django 4.1.3 on 2023-02-13 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tiers', '0004_tier_valid'),
    ]

    operations = [
        migrations.AddField(
            model_name='individualwinrate',
            name='game_count',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='movewinrate',
            name='game_count',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='opponentwinrate',
            name='game_count',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='teammatewinrate',
            name='game_count',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='terawinrate',
            name='game_count',
            field=models.PositiveIntegerField(default=1),
        ),
    ]