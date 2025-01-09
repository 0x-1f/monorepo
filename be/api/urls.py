from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet, PongViewSet

router = DefaultRouter()
router.register(r'items', ItemViewSet)
# router.register(r'users', UsersViewSet, basename="users")
router.register(r'pong', PongViewSet, basename="pong")
# router.register(r'rsp', RSPViewSet, basename="rsp")

urlpatterns = [
	path('api/', include(router.urls)),
]
