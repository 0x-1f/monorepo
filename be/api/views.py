import requests
from django.shortcuts import redirect
from django.http import JsonResponse, Http404
from django.conf import settings

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework import generics
from django.db.models import Q

from .models import Item
from games.models import PongGame, RPSGame
from user.models import Users
from .serializers import ItemSerializer
from games.serializers import PongSerializer, RPSSerializer
from user.views import UsersViewSet
from login.views import IntraAuthViewSet

class ItemViewSet(viewsets.ModelViewSet):
	queryset = Item.objects.all()
	serializer_class = ItemSerializer

class PongHistoryView(generics.ListAPIView):
    serializer_class = PongSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']  # URL에서 사용자 ID를 가져옵니다.
        return PongGame.objects.filter(
            Q(winner__user_id=user_id) | Q(loser__user_id=user_id)
        ).order_by('created_date')

class RPSHistoryView(generics.ListAPIView):
    serializer_class = RPSSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']  # URL에서 사용자 ID를 가져옵니다.
        return RPSGame.objects.filter(
            Q(player1__user_id=user_id) | Q(player2__user_id=user_id)
        ).order_by('created_date')
