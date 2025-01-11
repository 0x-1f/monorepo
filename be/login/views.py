import requests

from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.crypto import get_random_string
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

        try:
            jwt_token = create_jwt_token(user_profile, settings.JWT_SECRET_KEY, 3)
        except Exception as e:
            return JsonResponse({"error": f"[Failed to create JWT token]: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        send_and_save_verification_code(user_profile)
        # redircet with cookie
        return JsonResponse({'message': 'Verification code sent to email in intra'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="verify")
    def verify_code(self, request):
        code = request.data.get('code')
        if not code:
            return JsonResponse({'error': f"[Verification code is required]"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_email = request.data.get('email')
            user = Users.objects.get(email=user_email)

            if user.verification_code == code:
                jwt_token = create_jwt_token(user, settings.JWT_SECRET_KEY, 3)
                return JsonResponse({'token': jwt_token}, status=status.HTTP_200_OK)
            else:
                return JsonResponse({'error': 'Verification code is invalid'}, status=status.HTTP_400_BAD_REQUEST)
        except Users.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': f"[{e.__class__.__name__}] {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def send_and_save_verification_code(user):
    verification_code = get_random_string(length=6)
    user.verification_code = verification_code

    mail_subject = "0x-1f 이메일 인증 코드입니다."
    message = f'당신의 인증 코드는 {verification_code} 입니다.'
    send_mail(mail_subject, message, settings.SMTP_ID, [user.email])

def create_jwt_token(user: Users, secret_key, expire_days:int):
    try:
        payload = {
            'user_email': user.email,
            'exp': datetime.utcnow() + timedelta(days=expiration_days),
        }
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        token = token.decode('utf-8') if isinstance(token, bytes) else token
        return token
    except Exception as e:
        raise Exception(f"[{e.__class__.__name__}] {str(e)}")

# class CodeVerificationView(viewsets.ModelViewSet):
#     def create(self, request):
#         try:
#             user = validate_jwt_token_and_get_user(request, settings.JWT_SECRET_KEY)
#             verification_code = get_request_body_value(request, 'code')
#             intra_id = user.intra_id
#             is_new = True if intra_id is None else False

#             if user.verification_code == verification_code:
#                 jwt_token = create_jwt_token(user, JWT_AUTH_sECRET_KEY, 7)
                
#         except Exception as e:
#             return JsonResponse({"error": f"[{e.__class__.__name__}] {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)