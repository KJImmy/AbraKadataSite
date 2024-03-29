"""AbraKadataSite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from rest_framework.documentation import include_docs_urls

from pages.views import home_view,about_view,support_view,reports_view

urlpatterns = [
    path('docs/', include_docs_urls(title='My API service'), name='api-docs'),
    path('games/',include('games.urls')),
    path('user/',include('users.urls')),
    path('formats/',include('tiers.urls')),
    path('api-auth/',include('rest_framework.urls')),
    path('admin/',admin.site.urls),
    path('',home_view,name='home'),
    path('about/',about_view,name='about'),
    path('support/',support_view,name='support'),
    path('reports/',reports_view,name='reports'),
]
