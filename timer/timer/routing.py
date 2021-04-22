from channels.routing import ProtocolTypeRouter, URLRouter
import timerapp.routing
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator


application = ProtocolTypeRouter({
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                timerapp.routing.websocket_urlpatterns
            )
        ),
    ),
})