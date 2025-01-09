from django.urls import path
from .consumers import PongConsumer

websocket_urlpatterns = [
    path('ws/pong/<str:session_id>', PongConsumer.as_asgi()),  # WebSocket 경로 설정
]
