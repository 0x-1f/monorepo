from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import IntraAuthViewSet

router = DefaultRouter()
router.register(r'auth', IntraAuthViewSet, basename="intra_auth")

urlpatterns = [
	path('', include(router.urls)),
]