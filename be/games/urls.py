from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import PongViewSet, RPSViewSet

router = DefaultRouter()
router.register(r'pong', PongViewSet)
router.register(r'rps', RPSViewSet, basename='rps')

urlpatterns = [
	path('', include(router.urls)),
]
