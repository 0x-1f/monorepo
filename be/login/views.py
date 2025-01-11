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

class IntraAuthViewSet(viewsets.ModelViewSet):
	@action(detail=False, methods=["get"], url_path="login")
	def login(self, request):
		target_url = (f"{AUTH_URL}?client_id={CLIENT_UID}&redirect_uri={CALLBACK_URI}&response_type=code")
		return redirect(target_url)

	@action(detail=False, methods=["get"], url_path="callback")
	def callback(self, request):
		try:
			code = request.GET.get('code')
			access_token = self.get_access_token(code)
			intra_id = self.get_intra_id(access_token)
			user = self.get_or_create_user(intra_id)
			auth_token = self.create_jwt_token(user)
			print("here")
			response = redirect(CALLBACK_URI)
			response.set_cookie('jwt', auth_token)
			return response
		except Exception as e:
			return JsonResponse({'error': f"[{e.__class__.__name__}] {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

	def get_access_token(self, code):
		response = requests.post(
			self.token_api,
			data = {
				"grant_type": "authorization_code",
				"client_id": API_UID,
				"client_secret": API_SECRET,
				"code": code,
				"redirect_uri": REDIRECT_URI,
			}
		)
		if response.status_code != 200 or "error" in response.json():
			raise RequestException("Failed to retrieve access token")
		return response.json().get("access_token")

	def get_intra_id(self, access_token):
		response = requests.get(
			self.userinfo_api,
			headers = {"Authorization": f"Bearer {access_token}"}
		)
		if response.status_code != 200:
			raise GetDataException("Failed to retrieve Intra42 user information")
		return response.json().get("intra_id")

	def get_or_create_user(self, intra_id):
		try:
			return Users.objects.get(intra_id = intra_id)
		except Users.DoesNotExist:
			return Users.objects.create_user(intra_id=intra_id)

	def create_jwt_token(self, user):
		try:
			payload = {
				"intra_id": user.intra_id,
				"exp": datetime.utcnow() + timedelta(minutes=5),
			}
			token = jwt.encode(payload, settings.JWT_AUTH_SECRET_KEY, algorithm="HS256")
			return token.decode("utf-8") if isinstance(token, bytes) else token
		except Exception as e:
			raise TokenCreateException(f"[{e.__class__.__name__}] {e}")

	def get_redirect_url(self, auth_token):
		return API_BASE_URL + "register?" + urlencode({"token": auth_token})