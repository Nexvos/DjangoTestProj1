from channels.generic.websocket import WebsocketConsumer
from .models import Game

class DataConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
    def disconnect(self, close_code):
        pass
    def receive(self):
        qs = game.bet_set.all()
        total_bet = 0
        for bet in qs:
            total_bet += bet.amount
        self.send(text_data= {
            'total bet': message,
            'game_data': qs
        })
