from django.contrib import admin
from django.urls import path,include

from .views import dashboard_view,register_view,submit_showdown_name_view,submit_game_view,\
					stats_view,breakdown_view
urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
	path('dashboard/',dashboard_view,name='dashboard'),
	path('register/',register_view,name='register'),
	path('showdown-username/',submit_showdown_name_view,name='psusername'),
	path('submit-game/',submit_game_view,name='uploadgame'),
	path('stats/',stats_view,name='stats'),
]