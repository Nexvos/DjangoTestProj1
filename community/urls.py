from django.urls import path
from . import views
from userbetting.views import index, lazy_load_games

app_name = 'community'
urlpatterns = [
    # ex: /betting/
    path('', views.communityHome, name='communityHome'),
    path('search/', views.communitySearch, name='communitySearch'),
    path('create/', views.communityCreate, name='communityCreate'),
    path('<int:community_id>/', index, name='communityPage'),
    # path('<int:community_id>/lazy_load/', lazy_load_games, name='communityLazyLoad'),
    path('<int:community_id>/invite/', views.invitePage, name='invitePage'),
    path('<int:community_id>/admin/', views.adminPageOptions, name='adminPage'),
    path('<int:community_id>/admin/games/edit', views.adminPageEditGames, name='adminPageEditGames'),
    path('<int:community_id>/admin/games/add', views.adminPageAddGames, name='adminPageAddGames'),
    path('<int:community_id>/admin/tournaments', views.adminPageTournaments, name='adminPageTournaments'),
    path('<int:community_id>/admin/members', views.adminPageMembers, name='adminPageMembers'),
    path('<int:community_id>/tournaments/', views.tournament_list_view, name='tournament_list_view'),
    path('<int:community_id>/tournaments/<int:tournament_id>/', views.tournament_view, name='tournament_view'),
    path('<int:community_id>/<int:betting_group_id>/', views.detail, name='detail'),
    path('<int:community_id>/completed-games/', views.completed_game_list_view, name='completed_games_list_view'),

]