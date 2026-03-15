import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'futsal_management.settings')
django.setup()

# This must be called before importing anything that uses models
django_asgi_app = get_asgi_application()

# Now we can safely import routing
from chat.routing import websocket_urlpatterns

application = ProtocolTypeRouter(
   {
      "http": django_asgi_app,
      "websocket": URLRouter(websocket_urlpatterns)
   }
)