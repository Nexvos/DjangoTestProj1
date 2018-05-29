from django.urls import path

from . import views

app_name = 'userBetting'
urlpatterns = [
    # ex: /betting/
    path('', views.index, name='index'),
    path('test/', views.testPage, name='test'),
    # ex: /betting/5/
    path('<int:game_id>/', views.detail, name='detail'),
    # ex: /polls/5/results/
    path('<int:game_id>/results/', views.results, name='results'),
    # ex: /polls/5/vote/
    path('<int:game_id>/vote/', views.vote, name='vote'),
]