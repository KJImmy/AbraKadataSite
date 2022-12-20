from django.contrib import admin
from django.urls import path

from .views import format_base_view,formats_view,format_pokemon_view
urlpatterns = [
	path('',formats_view,name='formats'),
	path('gen<int:generation><tier_name>/',format_base_view,name='format_base'),
	path('gen<int:generation><tier_name>/<pokemon_unique_name>',format_pokemon_view,name='format_pokemon')
]