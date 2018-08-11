from django.shortcuts import render
from userbetting.models import Game, Tournament, Team
from .adminBettingFunctions import Add_new_tournament

# Create your views here.
def adminDashboard(request):
    context = {

    }
    return render(request, 'BettingAdmin/admin_dashboard.html', context)
def addTournament(request):
    Add_new_tournament("1")
    context = {
        'match_data': "match_data"
    }
    return render(request, 'BettingAdmin/add-tournament.html', context)