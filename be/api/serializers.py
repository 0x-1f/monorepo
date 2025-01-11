from rest_framework import serializers
from .models import Item

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

# class PongSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PongGame
#         fields = '__all__'

# class RSPSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = RSPGame
#         fields = '__all__'
