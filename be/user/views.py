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
		return redirect(auth_url)

	@action(detail=False, methods=["get", "post"], url_path="callback")
	def callback(self, request):
		# 인가 코드로 액세스 토큰 요청하기
		code = request.GET.get("code") # Query String 형태

		token_data = {
			"grant_type": "authorization_code",
			"client_id": settings.API_UID,
			"client_secret": settings.API_SECRET,
			"code": code,
			"redirect_uri": settings.REDIRECT_URI,
		}

		token_request = requests.post(settings.TOKEN_URL,data=token_data)
		token_request_json = token_request.json()
		error = token_request_json.get("error")

		if error is not None:
			raise JSONDecodeError(error)

		access_token = token_request_json.get("access_token")
		refresh_token = token_request_json.get("refresh_token")

		# 발급 된 인가 코드로 액세스 토큰으로 데이터를 요청
		headers = {"Authorization": f"Bearer {access_token}"}

		user_response = requests.get(f"{settings.API_BASE_URL}me", headers=headers)
		user_response_json = requests.get(f"{settings.API_BASE_URL}me", headers=headers).json()
		response_status = user_response.status_code

		if response_status != 200:
			return JsonResponse({"status": 400, "message": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)

		user_profile, created = Users.objects.update_or_create(
			intra_id = user_response_json.get("login"),
			defaults = {
				"refresh_token": refresh_token,
				"access_token": access_token,
			},
		)
		request.session['access_token'] = access_token
		request.session['refresh_token'] = refresh_token

		response_http = HttpResponseRedirect("http://localhost/main")
		response_http.set_cookie("intra_id", user_profile.intra_id)
		response_http.set_cookie("access_token", access_token)
		return response_http

