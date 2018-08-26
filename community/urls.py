from django.urls import path
from . import views
from userbetting.views import index

app_name = 'community'
urlpatterns = [
    # ex: /betting/
    path('', views.communityHome, name='communityHome'),
    path('<int:community_id>/', index, name='communityPage'),
    path('<int:community_id>/invite/', views.invitePage, name='invitePage'),
    path('<int:community_id>/admin/', views.adminPage, name='adminPage'),
    path('<int:community_id>/tournaments/', views.tournament_list_view, name='tournament_list_view'),
    path('<int:community_id>/tournaments/<int:tournament_id>/', views.tournament_view, name='tournament_view'),
    path('<int:community_id>/<int:betting_group_id>/', views.detail, name='detail'),
    path('<int:community_id>/completed-games/', views.completed_game_list_view, name='completed_games_list_view'),

]