from rest_framework import serializers
from user.models import Users
from .models import PongGame, RPSGame

class PongSerializer(serializers.ModelSerializer):
    winner_intra_id = serializers.CharField(source='winner.intra_id')
    loser_intra_id = serializers.CharField(source='loser.intra_id')

    class Meta:
        model = PongGame
        fields = ['pong_id', 'created_date', 'status', 'type','winner_intra_id', 'loser_intra_id', 'winner_score', 'loser_score']

class PongSerializerHistory(serializers.ModelSerializer):
    winner_intra_id = serializers.CharField(source='winner.intra_id')
    loser_intra_id = serializers.CharField(source='loser.intra_id')
    date = serializers.DateTimeField(source='created_date', format="%Y-%m-%d", read_only=True)
    opponent = serializers.SerializerMethodField()
    result = serializers.SerializerMethodField()

    class Meta:
        model = PongGame
        fields = ['pong_id', 'date', 'opponent', 'result', 'winner_intra_id', 'loser_intra_id', 'winner_score', 'loser_score']

    def get_opponent(self, obj):
        intra_id = self.get_intra_id()
        if obj.winner.intra_id == intra_id:
            return obj.loser.intra_id if obj.loser else None
        elif obj.loser.intra_id == intra_id:
            return obj.winner.intra_id if obj.winner else None
        return None

    def get_result(self, obj):
        intra_id = self.get_intra_id()
        if obj.winner.intra_id == intra_id:
            return "Win"
        return "Lose"

    def get_intra_id(self):
        request = self.context.get('request')
        path = request.path
        parts = path.split('/')

        intra_id = parts[parts.index('pong') + 1]
        return intra_id


class RPSSerializer(serializers.ModelSerializer):
    player1_intra_id = serializers.CharField(source='player1.intra_id')
    player2_intra_id = serializers.CharField(source='player2.intra_id')

    class Meta:
        model = RPSGame
        fields = ['rps_id', 'created_date', 'status', 'result', 'player1_intra_id', 'player2_intra_id', 'player1_choice', 'player2_choice']

class RPSSerializerHistory(serializers.ModelSerializer):
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
        if obj.result == "player1 draw, player2 draw":
            return "Draw"
        if obj.player1.intra_id == intra_id and obj.result == "player1 win, player2 lose":
            return "Win"
        elif obj.player2.intra_id == intra_id and obj.result == "player1 lose, player2 win":
            return "Win"
        return "Lose"

    def get_intra_id(self):
        request = self.context.get('request')
        path = request.path
        parts = path.split('/')

        intra_id = parts[parts.index('rps') + 1]
        return intra_id
