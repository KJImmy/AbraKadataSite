from django.urls import path
from .views import link_submission

urlpatterns = [
	path('',link_submission),
]