from __future__ import absolute_import, unicode_literals
from DjangoTestProj1.celery import app
from .models import Game
from decimal import *

TWOPLACES = Decimal(10) ** -2

@app.task
def pay_bets():
    games = Game.objects.all()
    for game in games:
        if(game.status == game.finished_confirmed):
            game_total = Decimal(0.00)
            game_winning_bet_total = Decimal(0.00)
            bets = game.game_bets.all()
            if bets:
                for bet in bets:
                    game_total += bet.amount

                    if (game.winning_team == game.team_a_winner and bet.chosen_team == game.team_a) or (game.winning_team == game.team_b_winner and bet.chosen_team == game.team_b):
                        game_winning_bet_total += bet.amount
                # 8% taken from the winnings (10% of the bets made for the losing team)
                game_total_reduced = ((game_total - game_winning_bet_total)/100)*90+game_winning_bet_total
                winning_ratio = game_total_reduced / game_winning_bet_total
                for bet in bets:
                    if(bet.status == bet.open):
                        user = bet.user
                        user_profile = user.profile
                        if(game.winning_team == game.team_a_winner and bet.chosen_team == game.team_a) or (game.winning_team == game.team_b_winner and bet.chosen_team == game.team_b):
                            user_profile.withdrawable_bank += (bet.amount * winning_ratio).quantize(TWOPLACES)
                            user_profile.save()

                            bet.winnings = (bet.amount * winning_ratio).quantize(TWOPLACES)
                            bet.status = bet.paid
                        else:
                            bet.status = bet.lost

                        bet.save()
            game.status = game.finished_paid
            game.save()







