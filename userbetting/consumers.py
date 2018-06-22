from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Game, Bet, Team
from django.shortcuts import get_object_or_404
import json
from .forms import BetForm
from django import forms

class DataConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.room_group_name = 'chat_%s' % self.game_id
        self.user = self.scope["user"]
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

            game = get_object_or_404(Game, pk=self.game_id)
            team = get_object_or_404(Team, name=chosenTeam)
            print("team is a team")
            print(self.user.profile.bank)
            if game.team_a == team or game.team_b == team:
                if amountBid <= self.user.profile.bank:
                    if self.user.profile.non_withdrawable_bank >= amountBid:
                        self.user.profile.non_withdrawable_bank = self.user.profile.non_withdrawable_bank - amountBid
                        self.user.profile.save()
                    else:
                        amountBid = amountBid - self.user.profile.non_withdrawable_bank
                        self.user.profile.non_withdrawable_bank = 0
                        self.user.profile.withdrawable_bank = self.user.profile.withdrawable_bank - amountBid
                        self.user.profile.save()

                    newBet = Bet(user= self.user, game= game,chosen_team=team, amount= amountBid)
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
        self.game = get_object_or_404(Game, pk=self.game_id)
        data = '['
        qs = self.game.bet_set.all()
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
