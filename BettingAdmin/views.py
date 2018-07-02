from django.shortcuts import render
from userbetting.models import Game

# Create your views here.
def addTournament(request):
    games = Game.objects.all()
    # pay out bets function
    # pay_bets()

    # Rank users function

    context = {
        'games':games

    }
    return render(request, 'BettingAdmin/add-tournament.html', context)