import requests

from django.shortcuts import redirect
from django.http import JsonResponse
from django.conf import settings

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action, api_view

from user.models import Users
from user.serializers import UsersSerializer

CALLBACK_URI = settings.REDIRECT_URI
AUTH_URL = settings.AUTH_URL
TOKEN_URL = settings.TOKEN_URL
API_BASE_URL = settings.API_BASE_URL

CLIENT_UID = settings.API_UID
CLIENT_SECRET = settings.API_SECRET

class IntraLoginView(viewsets.ModelViewSet):
	def get(self, request):
		target_url = f"{AUTH_URL}?client_id={CLIENT_UID}&redirect_uri={CALLBACK_URI}&response_type=code"
		return redirect(target_url)

class IntraCallbackView(viewsets.ModelViewSet):
	def get(self, request):
		try:
			code = request.GET.get('code')
			access_token = self.get_access_token(code)
			# user = Users.objects.get(intra_id=)
	pass

class Verification(viewsets.ModelViewSet):
	pass