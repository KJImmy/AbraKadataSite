from django.contrib import admin
from django.urls import path

from .views import format_base_view,formats_view,format_pokemon_view,format_teams_view,format_team_breakdown_view,format_cores_view,\
					format_core_breakdown_view,format_base_view_test

urlpatterns = [
	path('',formats_view,name='formats'),
	path('gen<int:generation><tier_name>/',format_base_view,name='format_base'),
	path('gen<int:generation><tier_name>/filter/',format_base_view_test,name='format_base_test'),
	path('gen<int:generation><tier_name>/teams/',format_teams_view,name='format_teams'),
	path('gen<int:generation><tier_name>/teams/<int:team_id>/',format_team_breakdown_view,name='format_team_breakdown'),
	path('gen<int:generation><tier_name>/cores/',format_cores_view,name='format_cores'),
	path('gen<int:generation><tier_name>/cores/<int:core_id>/',format_core_breakdown_view,name='format_core_breakdown'),
	path('gen<int:generation><tier_name>/<pokemon_unique_name>/',format_pokemon_view,name='format_pokemon'),
]