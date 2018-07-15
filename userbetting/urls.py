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
]