from django.test import TestCase
from .models import Profile
from userbetting.models import Bet, Team, Game
from django.utils import timezone
import datetime
from django.contrib.auth.models import User
from .tasks import *
from userbetting.tasks import *
from django.shortcuts import get_object_or_404
from decimal import *

# Create your tests here.
class RankingTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        login = self.client.login(username='testuser', password='12345')
        user_2 = User.objects.create_user(username='testuser2', password='12345')
        user_3 = User.objects.create_user(username='testuser3', password='12345')
        user_4 = User.objects.create_user(username='testuser4', password='12345')

        team_a = Team(name="team_a")
        team_a.save()
        team_b = Team(name="team_b")
        team_b.save()
        time = timezone.now() + datetime.timedelta(days=30)
        game = Game(team_a=team_a, team_b=team_b, winning_team=Game.team_a_winner, status=Game.finished_confirmed,
                    game_date=time)
        game.save()

        bet_1 = Bet(user=self.user, game=game, chosen_team=team_a, amount=55)
        bet_1.save()
        bet_2 = Bet(user=self.user, game=game, chosen_team=team_b, amount=66)
        bet_2.save()
        bet_3 = Bet(user=self.user, game=game, chosen_team=team_a, amount=22)
        bet_3.save()
        bet_4 = Bet(user=user_2, game=game, chosen_team=team_a, amount=20)
        bet_4.save()
        bet_5 = Bet(user=user_2, game=game, chosen_team=team_a, amount=30)
        bet_5.save()
        bet_6 = Bet(user=user_3, game=game, chosen_team=team_b, amount=30)
        bet_6.save()
        bet_7 = Bet(user=user_3, game=game, chosen_team=team_a, amount=20)
        bet_7.save()
        bet_8 = Bet(user=user_4, game=game, chosen_team=team_a, amount=12)
        bet_8.save()
        bet_9 = Bet(user=user_4, game=game, chosen_team=team_b, amount=13)
        bet_9.save()
        bet_10 = Bet(user=user_4, game=game, chosen_team=team_a, amount=24)
        bet_10.save()

        pay_bets()

        #self.user has £77 and is 1st
        #user_2 has £50 and is 2nd
        #user_3 has £20 and is 4th
        #user_4 has £36 and is 3rd

        total_winnings = Decimal(((bet_2.amount + bet_6.amount + bet_9.amount)/100)*90)
        total_winning_bet = Decimal(bet_1.amount + bet_3.amount + bet_4.amount + bet_5.amount + bet_7.amount + bet_8.amount + bet_10.amount)
        global winning_ratio
        winning_ratio =total_winnings/total_winning_bet

    def test_profile_creation(self):
        user_2 = User.objects.get(username='testuser2')
        self.assertEqual(user_2.profile.colour, "D3D3D3")

    def test_ranking(self):

        user_1 = User.objects.get(username='testuser')
        user_2 = User.objects.get(username='testuser2')
        user_3 = User.objects.get(username='testuser3')
        user_4 = User.objects.get(username='testuser4')

        rank_users_winnings()

        TWOPLACES = Decimal(10) ** -2
        user_1_expected_winnings = (Decimal(55.00)*winning_ratio).quantize(TWOPLACES) + (Decimal(22.00)*winning_ratio).quantize(TWOPLACES) +77
        user_2_expected_winnings = (Decimal(20.00) * winning_ratio).quantize(TWOPLACES) + (Decimal(30.00) * winning_ratio).quantize(TWOPLACES) + 50
        user_3_expected_winnings = (Decimal(20.00) * winning_ratio).quantize(TWOPLACES) + 20
        user_4_expected_winnings = (Decimal(12.00) * winning_ratio).quantize(TWOPLACES) + (Decimal(24.00) * winning_ratio).quantize(TWOPLACES) + 36

        self.assertEqual(user_1.profile.withdrawable_bank, user_1_expected_winnings)
        self.assertEqual(user_2.profile.withdrawable_bank, user_2_expected_winnings)
        self.assertEqual(user_3.profile.withdrawable_bank, user_3_expected_winnings)
        self.assertEqual(user_4.profile.withdrawable_bank, user_4_expected_winnings)
        self.assertEqual(user_1.profile.ranking, 1)
        self.assertEqual(user_2.profile.ranking, 2)
        self.assertEqual(user_3.profile.ranking, 4)
        self.assertEqual(user_4.profile.ranking, 3)











# Create your tests here.
# withdrawable_bank = 100
# nonwithdrawable_bank = 50
#
# bank_total = withdrawable_bank + nonwithdrawable_bank
#
# amount = 160
#
# if bank_total > amount:
#     if nonwithdrawable_bank > amount:
#         nonwithdrawable_bank = nonwithdrawable_bank - amount
#     else:
#         amount = amount - nonwithdrawable_bank
#         nonwithdrawable_bank = 0
#         withdrawable_bank = withdrawable_bank - amount
#     bank_total = withdrawable_bank + nonwithdrawable_bank
#     amount = 0
# else:
#     raise Exception('My error!')
#
# print("total bank: ", bank_total)
# print("Withdrawable bank: ", withdrawable_bank)
# print("Nonwithdrawable bank: ", nonwithdrawable_bank)
