# Generated by Django 4.1.3 on 2023-05-26 17:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tiers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=1000)),
                ('tier', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reports_of_tier', to='tiers.tier')),
            ],
        ),
    ]
