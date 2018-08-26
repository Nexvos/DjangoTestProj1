from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Game, Bet, Team, BettingGameGroup
from profiles.models import Wallet
from django.shortcuts import get_object_or_404
import json
from .forms import BetForm
from django import forms

class DataConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.betting_group_id = self.scope['url_route']['kwargs']['betting_group_id']
        self.room_group_name = 'chat_%s' % self.betting_group_id
        self.user = self.scope["user"]
        print(self.betting_group_id)
        self.game_bgg = get_object_or_404(BettingGameGroup, pk=self.betting_group_id)
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        chosenTeamJson = text_data_json['chosenTeam']
        amountBidJson = text_data_json['amountBid']

        form_data = {
            "chosen_team": chosenTeamJson,
            "amount": amountBidJson
                     }
        form = BetForm(form_data)
        if form.is_valid():
            chosenTeam = form.cleaned_data['chosen_team']
            amountBid = form.cleaned_data['amount']

            team = get_object_or_404(Team, name=chosenTeam)
            user_wallet = Wallet.objects.get(profile=self.user.profile, group=self.game_bgg.group)
            if self.game_bgg.game.team_a == team or self.game_bgg.game.team_b == team:
                if amountBid <= user_wallet.bank:
                    if user_wallet.non_withdrawable_bank >= amountBid:
                        user_wallet.non_withdrawable_bank = user_wallet.non_withdrawable_bank - amountBid
                        user_wallet.save()
                    else:
                        amountBid = amountBid - user_wallet.non_withdrawable_bank
                        user_wallet.non_withdrawable_bank = 0
                        user_wallet.withdrawable_bank = user_wallet.withdrawable_bank - amountBid
                        user_wallet.save()

                    newBet = Bet(user= self.user, betting_group= self.game_bgg, chosen_team=team, amount= amountBid)
                    newBet.save()

                    message = "nothing"

                    # Send message to room group
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'send_update',
                            'message': message
                        }
                    )
                else:
                    raise forms.ValidationError("User does not have the money to make this bet")
            else:
                raise forms.ValidationError("Amount Bid or Team Value is not valid")
        else:
            raise forms.ValidationError("Form is not valid")

    async def send_update(self, event):
        message = event['message']
        self.game_bgg = get_object_or_404(BettingGameGroup, pk=self.betting_group_id)
        data = '['
        qs = self.game_bgg.game_bets.all()
        total_bet = 0
        count = 0
        for bet in qs:
            total_bet += bet.amount
        for bet in qs:
            data += '{"name": "'+ str(bet.user) + '", "amount": ' + str(bet.amount) + ', "percent": ' + str((bet.amount / total_bet)*100) + ', "team": "' + str(bet.chosen_team) + '", "colour": "' + "#"+ str(bet.user.profile.colour) + '"}'
            count += 1
            if count != qs.count():
                data += ","
        data += ']'
        total_bet = str(total_bet)
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': data,
            'total_bet': total_bet
        }))
