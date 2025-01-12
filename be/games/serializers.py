from rest_framework import serializers
from .models import PongGame, RPSGame

class PongSerializer(serializers.ModelSerializer):
    winner_intra_id = serializers.CharField(source='winner.intra_id')
    loser_intra_id = serializers.CharField(source='loser.intra_id')

    class Meta:
        model = PongGame
        fields = ['pong_id', 'created_date', 'status', 'type','winner_intra_id', 'loser_intra_id', 'winner_score', 'loser_score']

class RPSSerializer(serializers.ModelSerializer):
    player1_intra_id = serializers.CharField(source='player1.intra_id')
    player2_intra_id = serializers.CharField(source='player2.intra_id')
    date = serializers.DateTimeField(source='created_date', format="%Y-%m-%d", read_only=True)
    opponent = serializers.SerializerMethodField()
    result = serializers.SerializerMethodField()

    class Meta:
        model = RPSGame
        fields = ['rps_id', 'date', 'opponent', 'result', 'player1_intra_id', 'player2_intra_id', 'player1_choice', 'player2_choice']

    def get_opponent(self, obj):
        user = self.context['request'].user
        if obj.player1 == user:
            return obj.player2.intra_id
        elif obj.player2 == user:
            return obj.player1.intra_id
        return None

    def get_result(self, obj):
        user = self.context['request'].user
        if obj.result == "draw":
            return "Draw"
        if obj.player1 == user and obj.result == "player1":
            return "Win"
        elif obj.player2 == user and obj.result == "player2":
            return "Win"
        return "Lose"
