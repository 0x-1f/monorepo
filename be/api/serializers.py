from rest_framework import serializers
from .models import Item, PongGame

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Users
#         fields = ["id", "intra_id"]

class PongSerializer(serializers.ModelSerializer):
    class Meta:
        model = PongGame
        fields = '__all__'

# class RSPSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = RSPGame
#         fields = '__all__'
