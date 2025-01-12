from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet
from login.views import IntraAuthViewSet
from user.views import UsersViewSet
from games.views import RPSViewSet
from .views import PongHistoryView, RPSHistoryView

router = DefaultRouter()
# router.register(r'pong', PongViewSet, basename="pong")
router.register(r'auth', IntraAuthViewSet, basename="login")
router.register(r'rps', RPSViewSet, basename="rps")
router.register(r'users', UsersViewSet, basename="users")

urlpatterns = [
	path('api/', include(router.urls)),
	path('api/pong/<int:user_id>/history/', PongHistoryView.as_view(), name='pong-game-history'),
	path('api/rps/<int:user_id>/history/', RPSHistoryView.as_view(), name='rps-game-history'),
]
