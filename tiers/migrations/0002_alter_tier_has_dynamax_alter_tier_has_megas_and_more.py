# Generated by Django 4.1.3 on 2022-12-05 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tiers', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tier',
            name='has_dynamax',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='tier',
            name='has_megas',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='tier',
            name='has_tera',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='tier',
            name='has_zmoves',
            field=models.BooleanField(default=False),
        ),
    ]
