# Generated by Django 4.1.3 on 2023-02-10 00:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tiers', '0003_individualwinrate_ranked_movewinrate_ranked_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tier',
            name='valid',
            field=models.BooleanField(default=True),
        ),
    ]
