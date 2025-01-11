from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet
from login.views import IntraAuthViewSet
from user.views import UsersViewSet

router = DefaultRouter()
# router.register(r'pong', PongViewSet, basename="pong")
router.register(r'auth', IntraAuthViewSet, basename="login")
# router.register(r'rsp', RSPViewSet, basename="rsp")
router.register(r'users', UsersViewSet, basename="rsp")

urlpatterns = [
	path('api/', include(router.urls)),
]
