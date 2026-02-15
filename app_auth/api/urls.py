from django.contrib.auth import views as auth_views
from django.urls import path
from .views import (
    RegistrationView,
    ActivateView,
    LoginView,
    LogOutView,
    TokenRefreshView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path("activate/<str:uidb64>/<str:token>/", ActivateView.as_view(), name="activate"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogOutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("password_reset/", PasswordResetRequestView.as_view(), name="password_reset"),
    path(
        "password_confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
]
