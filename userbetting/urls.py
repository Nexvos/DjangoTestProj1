from django.urls import path

from . import views

app_name = 'userBetting'
urlpatterns = [
    # ex: /betting/
    path('', views.index, name='index'),
    path('test/', views.testPage, name='test'),
    # ex: /betting/5/
    path('lazy_load_games/', views.lazy_load_games, name='lazy_load_posts'),
]