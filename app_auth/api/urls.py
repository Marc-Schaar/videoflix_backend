from django.urls import path

from .views import RegistrationView, ActivateView, LoginView

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path("activate/<str:uidb64>/<str:token>/", ActivateView.as_view(), name="activate"),
    path("login/", LoginView.as_view(), name="login")
]
