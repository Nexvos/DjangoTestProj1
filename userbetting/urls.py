from django.urls import path

from . import views

app_name = 'userBetting'
urlpatterns = [
    # ex: /betting/
    path('', views.index, name='index'),
    path('test/', views.testPage, name='test'),
    # ex: /betting/5/
    path('<int:game_id>/', views.detail, name='detail'),
    # ex: /betting/5/
    path('tournament/<int:tournament_id>/', views.tournament_view, name='tournament_view'),
    path('lazy_load_games/', views.lazy_load_games, name='lazy_load_posts'),
    path('tournament-list/', views.tournament_list_view, name='tournament_list_view'),
    path('completed-games/', views.completed_game_list_view, name='completed_games_list_view'),
]