from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('query/<filter>', views.query, name='query'),
]
