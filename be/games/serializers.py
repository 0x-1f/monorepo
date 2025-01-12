from rest_framework import serializers
from user.models import Users
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
        intra_id = self.get_intra_id()
        if obj.player1.intra_id == intra_id:
            return obj.player2.intra_id if obj.player2 else None
        elif obj.player2.intra_id == intra_id:
            return obj.player1.intra_id if obj.player1 else None
        return None

    def get_result(self, obj):
        intra_id = self.get_intra_id()
        print(f"intra_id in result {intra_id}, obj result : {obj.result}", flush=True)
        if obj.result == "draw":
            return "Draw"
        if obj.player1.intra_id == intra_id and obj.result == "player1_win":
            return "Win"
        elif obj.player2.intra_id == intra_id and obj.result == "player2_win":
            return "Win"
        return "Lose"

    def get_intra_id(self):
        request = self.context.get('request')
        path = request.path
        parts = path.split('/')

        intra_id = parts[parts.index('rps') + 1]
        return intra_id