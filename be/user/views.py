import requests

from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.conf import settings

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action, api_view

from .models import Users
from .serializers import UsersSerializer

# Create your views here.
class UsersViewSet(viewsets.ModelViewSet):
	queryset = Users.objects.all()
	serializer_class = UsersSerializer

	@action(detail=False, methods=["get"], url_path="login")
	def login(self, request):
		auth_url = (f"{settings.AUTH_URL}?client_id={settings.API_UID}&redirect_uri={settings.REDIRECT_URI}&response_type=code")
		print(f"Redirecting to: {auth_url}")
		return redirect(auth_url)

	@action(detail=False, methods=["get", "post"], url_path="callback")
	def callback(self, request):
		code = request.GET.get("code")
		if not code:
			print("AUTHORIZATION CODE MISSING")
			return Response({"error"}, status=400)

		token_data = {
			"grant_type": "authorization_code",
			"client_id": settings.API_UID,
			"client_secret": settings.API_SECRET,
			"code": code,
			"redirect_uri": settings.REDIRECT_URI,
		}

		token_response = requests.post(settings.TOKEN_URL,data=token_data).json()
		access_token = token_response.get("access_token")
		refresh_token = token_response.get("refresh_token")

		headers = {"Authorization": f"Bearer {access_token}"}

		user_response = requests.get(f"{settings.API_BASE_URL}me", headers=headers).json()

		intra_id = user_response.get("login")
		if not intra_id:
			return Response("User maybe empty")
		user_profile, created = Users.objects.update_or_create(
			intra_id = user_response.get("login"),
			defaults = {
				"refresh_token": refresh_token,
			},
		)
# 인증성공하면 redirect to "baseURL/main"
		# return redirect("baseURL/main")
		return Response(
			{
				"message": "user profile saved successfully.",
				"user": user_profile.intra_id,
			}
		)

