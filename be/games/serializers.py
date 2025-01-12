from rest_framework import serializers
from .models import PongGame, RPSGame

class PongSerializer(serializers.ModelSerializer):
    winner_intra_id = serializers.CharField(source='winner.intra_id')
    loser_intra_id = serializers.CharField(source='loser.intra_id')

    class Meta:
        model = PongGame
        fields = ['pong_id', 'created_date', 'status', 'type','winner_intra_id', 'loser_intra_id', 'winner_scoer', 'loser_score']

class RPSSerializer(serializers.ModelSerializer):
    player1_intra_id = serializers.CharField(source='player1.intra_id')
    player2_intra_id = serializers.CharField(source='player2.intra_id')

    class Meta:
        model = RPSGame
        fields = ['pong_id', 'created_date', 'status', 'result', 'player1_intra_id', 'player2_intra_id', 'player1_choice', 'player2_choice']
