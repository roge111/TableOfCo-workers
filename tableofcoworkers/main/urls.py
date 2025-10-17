from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    
    path('', views.index),
    path('table/', views.table, name='table'),
    path('create_call/', views.create_call, name='create_call')
]
