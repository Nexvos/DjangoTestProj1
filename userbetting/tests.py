from django.test import TestCase
from .models import Game, Bet, Team
from django.utils import timezone
import datetime
from django.contrib.auth.models import User
from .tasks import *
from django.shortcuts import get_object_or_404

# Create your tests here.
class QuestionModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        login = self.client.login(username='testuser', password='12345')

        team_a = Team(name="team_a")
        team_a.save()
        team_b = Team(name="team_b")
        team_b.save()
        time = timezone.now() + datetime.timedelta(days=30)
        game = Game(team_a=team_a, team_b=team_b, winning_team=Game.team_a_winner, status=Game.finished_confirmed,
                    game_date=time)
        game.save()
        winning_bet = Bet(user=self.user, game=game, chosen_team=team_a, amount=20)
        winning_bet.save()
        losing_bet = Bet(user=self.user, game=game, chosen_team=team_b, amount=40)
        losing_bet.save()
        global game_id
        game_id= game.game_id

    def test_all_bets_paid(self):

        pay_bets()
        game = Game.objects.get(game_id=game_id)
        winning_bet = Bet.objects.get(game=game, chosen_team=game.team_a)
        losing_bet = Bet.objects.get(game=game, chosen_team=game.team_b)

        expected_winnings = winning_bet.amount + (losing_bet.amount/100)*90

        self.assertEqual(game.status,Game.finished_paid)
        self.assertEqual(winning_bet.status, Bet.paid)
        self.assertEqual(losing_bet.status, Bet.lost)
        self.assertEqual(winning_bet.winnings, expected_winnings)
        self.assertEqual(losing_bet.winnings, 0.00)