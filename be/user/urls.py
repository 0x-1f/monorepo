# from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import UsersViewSet

router = DefaultRouter()
# router.register(r'login', UsersViewSet, basename='login')
# router.register(r'callback', UsersViewSet, basename='callback')

urlpatterns = [
	# path('', include(router.urls)),
	path('login/', UsersViewSet.as_view({'get': 'login'}), name='login'),
	path('callback', UsersViewSet.as_view({'get': 'callback', 'post': 'callback'}), name='callback'),
]