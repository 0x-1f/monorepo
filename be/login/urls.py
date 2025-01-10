from django.urls import path

from .views import IntraLoginView, IntraCallbackView, Verification

urlpatterns = [
	path('intra/login/', IntraLoginView.as_view(), name="42login"),

	path('intra/callback/', IntraCallbackView.as_view(), name="42callback"),
	path('verify/', Verification.as_View(), name="verify_again"),
]