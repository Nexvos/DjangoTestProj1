from __future__ import absolute_import, unicode_literals
from DjangoTestProj1.celery import app
from .models import Game




@app.task
def pay_bets():
    games = Game.objects.all()

    for game in games:
        if(game.status == game.finished_confirmed):
            bets = game.bet_set.all()
            for bet in bets:
                if(bet.status == bet.open):
                    user = bet.user
                    user_profile = user.profile
                    if(game.winning_team == game.team_a_winner and bet.chosen_team == game.team_a) or (game.winning_team == game.team_b_winner and bet.chosen_team == game.team_b):
                        user_profile.bank += bet.amount
                        user_profile.save()
                        bet.status = bet.paid
                    else:
                        bet.status = bet.lost

                    bet.save()
            game.status = game.finished_paid
            game.save()







