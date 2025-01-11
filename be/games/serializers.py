from rest_framework import serializers
from .models import PongGame, RPSGame

class PongSerializer(serializers.ModelSerializer):
    class Meta:
        model = PongGame
        fields = '__all__'

class RPSSerializer(serializers.ModelSerializer):
    class Meta:
        model = RPSGame
        fields = '__all__'
