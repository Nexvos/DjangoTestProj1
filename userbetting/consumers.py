from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Game, Bet, Team
from django.shortcuts import get_object_or_404
import json

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
        print(text_data_json)
        chosenTeam = text_data_json['chosenTeam']
        amountBid = text_data_json['amountBid']
        print(chosenTeam)
        print(amountBid)

        newBet = Bet(user= self.user, game= get_object_or_404(Game, pk=self.game_id),chosen_team=get_object_or_404(Team, name=chosenTeam), amount= amountBid)
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

        print("recieved")

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
            data += '{"name": "'+ str(bet.user) + '", "amount": ' + str(bet.amount) + ', "percent": ' + str((bet.amount / total_bet)*100) + ', "team": "' + str(bet.chosen_team) +  '"}'
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
