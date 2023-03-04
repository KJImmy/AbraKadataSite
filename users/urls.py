from django.contrib import admin
from django.urls import path,include

from .views import dashboard_view,register_view
urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
	path('dashboard/',dashboard_view,name='dashboard'),
	path('register/',register_view,name='register')
]