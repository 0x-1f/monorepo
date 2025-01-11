import requests

from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.conf import settings

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action, api_view

from .models import Users
from .serializers import UsersSerializer

# Create your views here.
class UsersViewSet(viewsets.ModelViewSet):
	queryset = Users.objects.all()
	serializer_class = UsersSerializer
