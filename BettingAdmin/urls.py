from django.urls import path

from . import views

app_name = 'BettingAdmin'
urlpatterns = [
    # ex: /betting/
    path('', views.addTournament, name='addTournament'),

]