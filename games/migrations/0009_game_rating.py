# Generated by Django 4.1.3 on 2023-03-15 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0008_player_site_user_alter_usersubmittedgame_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='rating',
            field=models.PositiveIntegerField(null=True),
        ),
    ]