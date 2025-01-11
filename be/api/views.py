import requests
from django.shortcuts import redirect
from django.http import JsonResponse
from django.conf import settings

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action, api_view

from .models import Item, Users, PongGame
from .serializers import ItemSerializer, PongSerializer

class ItemViewSet(viewsets.ModelViewSet):
	queryset = Item.objects.all()
	serializer_class = ItemSerializer

class PongViewSet(viewsets.ModelViewSet):
	queryset = PongGame.objects.all()
	serializer_class = PongSerializer


# class RSPViewSet(viewsets.ModelViewSet):
#     queryset = RSPGame.objects.all()
#     serializer_class = RSPSerializer
