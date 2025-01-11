from django.urls import path
from .consumers import PongMatchConsumer, PongQueueConsumer, RPSMatchConsumer, RPSQueueConsumer

websocket_urlpatterns = [
    path('ws/pong/join/<str:intra_id>', PongQueueConsumer.as_asgi()),  # WebSocket 경로 설정
    path('ws/pong/match/<str:match_name>/<str:intra_id>', PongMatchConsumer.as_asgi()),
	path('ws/rps/join/<str:intra_id>', RPSQueueConsumer.as_asgi()),  # WebSocket 경로 설정
    path('ws/rps/match/<str:match_name>/<str:intra_id>', RPSMatchConsumer.as_asgi()),
]
