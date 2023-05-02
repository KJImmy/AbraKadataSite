# Generated by Django 4.1.3 on 2023-05-02 18:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0010_gameplayerrelation_personal_include'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPSUsernameRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('include', models.BooleanField(default=True)),
                ('ps_username', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='users_with_ps_name', to='games.player')),
                ('site_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ps_names_of_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
