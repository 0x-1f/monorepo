from rest_framework import serializers

class VerificationCodeSerializer(serializers.Serializer):
	token = serializers.CharField()