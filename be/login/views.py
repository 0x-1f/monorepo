import requests

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.http import urlencode

from rest_framework import viewsets, status
from rest_framework.decorators import action

from user.models import Users

CALLBACK_URI = settings.REDIRECT_URI
AUTH_URL = settings.AUTH_URL
TOKEN_URL = settings.TOKEN_URL
API_BASE_URL = settings.API_BASE_URL

CLIENT_UID = settings.API_UID
CLIENT_SECRET = settings.API_SECRET

class IntraAuthViewSet(viewsets.ModelViewSet):
    @action(detail=False, methods=["get"], url_path="login")
    def login(self, request):
        target_url = f"{AUTH_URL}?client_id={CLIENT_UID}&redirect_uri={CALLBACK_URI}&response_type=code"
        return redirect(target_url)

    @action(detail=False, methods=["get"], url_path="callback")
    def callback(self, request):
        code = request.GET.get('code')
        if not code:
            return JsonResponse({'error': f"[Auth code missing]"}, status=status.HTTP_400_BAD_REQUEST)
        token_data = {
            "grant_type": "authorization_code",
            "client_id": CLIENT_UID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "redirect_uri": CALLBACK_URI,
        }
        token_response = requests.post(TOKEN_URL, data=token_data).json()
        access_token = token_response.get("access_token")
        refresh_token = token_response.get("refresh_token")

        if not access_token:
            return JsonResponse({'error': f"[Access token missing]"}, status=status.HTTP_400_BAD_REQUEST)

        headers = {"Authorization": f"Bearer {access_token}"}

        try:
            user_response = requests.get(f"{API_BASE_URL}me", headers=headers)
            user_response.raise_for_status()
            user_data = user_response.json()
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": f"[Failed to fetch user data]: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        intra_id = user_data.get("login")
        email = user_data.get("email")
        if not intra_id:
            return JsonResponse({"error": f"[user data missing]"}, status=status.HTTP_400_BAD_REQUEST)

        user_profile, created = Users.objects.update_or_create(
            intra_id=intra_id,
            defaults={
                "refresh_token": refresh_token,
                "access_token": access_token,
                "email": email,
            }
        )

        # redircet with cookie
        response = redirect("https://localhost/main")
        response.set_cookie("refresh_token", "token valllllue")
        return response
