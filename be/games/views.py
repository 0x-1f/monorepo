from django.shortcuts import redirect
from django.http import JsonResponse
from django.conf import settings

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action, api_view

from .models import PongGame, RPSGame
from .serializers import PongSerializer, RPSSerializer

class PongViewSet(viewsets.ModelViewSet):
    queryset = PongGame.objects.all()
    serializer_class = PongSerializer


class RPSViewSet(viewsets.ModelViewSet):
    queryset = RPSGame.objects.all()
    serializer_class = RPSSerializer


