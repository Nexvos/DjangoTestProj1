from django.shortcuts import render
from userbetting.models import Game
from .adminBettingFunctions import get_future_match_data

# Create your views here.
def addTournament(request):
    games = Game.objects.all()
    # pay out bets function
    # pay_bets()
    data = get_future_match_data()
    # Rank users function

    context = {
        'match_data':data

    }
    return render(request, 'BettingAdmin/add-tournament.html', context)