# userbetting/routing.py
from django.conf.urls import url
from . import consumers

websocket_urlpatterns = [
    url(r'^ws/betting/<int:game_id>/', consumers.DataConsumer),
]
