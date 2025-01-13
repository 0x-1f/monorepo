from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from user.models import Users
from .models import PongGame, RPSGame
from .serializers import PongSerializer, RPSSerializer, RPSSerializerHistory, PongSerializerHistory

class PongViewSet(viewsets.ModelViewSet):
    queryset = PongGame.objects.all()
    serializer_class = PongSerializer

    def get_serializer_class(self):
        if self.action == 'history':
            return PongSerializerHistory
        return super().get_serializer_class()

    @action(detail=True, methods=['get'], url_path='history')
    def history(self, request, pk=None):
        serializer = PongSerializerHistory
        user = get_object_or_404(Users, intra_id=pk)
        if user is None:
            return JsonResponse({"message": "User not found"}, status=404)
        primary_key = user.user_id
        # type_filter = request.query_params.get('type', "")
        games = PongGame.objects.filter(Q(winner=user) | Q(loser=user))
        # games = games.filter(type=type_filter)
        serializer = self.get_serializer(games, many=True, context={'request': request})
        return Response(serializer.data)


class RPSViewSet(viewsets.ModelViewSet):
    queryset = RPSGame.objects.all()
    serializer_class = RPSSerializer

    def get_serializer_class(self):
        if self.action == 'history':
            return RPSSerializerHistory
        return super().get_serializer_class()

    @action(detail=True, methods=['get'], url_path='history')
    def history(self, request, pk=None):
        serializer = RPSSerializerHistory
        user = get_object_or_404(Users, intra_id=pk)
        if user is None:
            return JsonResponse({"message": "User not found"}, status=404)
        primary_key = user.user_id
        games = RPSGame.objects.filter(Q(player1=user) | Q(player2=user))
        serializer = self.get_serializer(games, many=True, context={'request': request})
        return Response(serializer.data)