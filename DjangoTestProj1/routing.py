# mysite/routing.py
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import userbetting.routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            userbetting.routing.websocket_urlpatterns
        )
    ),
})

#
# channel_routing = [
#     route('websocket.connect', ws_connect),
#     route('websocket.receive', ws_receive),
#     route('websocket.disconnect', ws_disconnect),
# ]