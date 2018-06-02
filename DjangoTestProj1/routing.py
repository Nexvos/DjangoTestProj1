# mysite/routing.py
from channels.routing import ProtocolTypeRouter

application = ProtocolTypeRouter({
    # (http->django views is added by default)
})
#
# channel_routing = [
#     route('websocket.connect', ws_connect),
#     route('websocket.receive', ws_receive),
#     route('websocket.disconnect', ws_disconnect),
# ]