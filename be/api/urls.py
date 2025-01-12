from django.urls import path, include

from rest_framework.routers import DefaultRouter

from login.views import IntraAuthViewSet
from user.views import UsersViewSet
from games.views import RPSViewSet, PongViewSet

router = DefaultRouter()
router.register(r'pong', PongViewSet, basename="pong")
router.register(r'auth', IntraAuthViewSet, basename="login")
router.register(r'rps', RPSViewSet, basename="rps")
router.register(r'users', UsersViewSet, basename="users")

urlpatterns = [
	path('api/', include(router.urls)),
]
