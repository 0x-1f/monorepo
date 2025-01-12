from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from user.models import Users
from .models import PongGame, RPSGame
from .serializers import PongSerializer, RPSSerializer

class PongViewSet(viewsets.ModelViewSet):
    queryset = PongGame.objects.all()
    serializer_class = PongSerializer


class RPSViewSet(viewsets.ModelViewSet):
    serializer_class = RPSSerializer
    queryset = RPSGame.objects.all()

    @action(detail=True, methods=['get'], url_path='history')
    def history(self, request, pk=None):
        user = get_object_or_404(Users, intra_id=pk)
        primary_key = user.user_id
        if user is None:
            return JsonResponse({"message": "User not found"}, status=404)
        games = RPSGame.objects.filter(Q(player1=user) | Q(player2=user))
        serializer = self.get_serializer(games, many=True, context={'request': request})
        return Response(serializer.data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

#날짜, 상대, 승패, 선택
