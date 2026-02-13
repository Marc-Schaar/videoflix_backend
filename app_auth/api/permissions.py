from rest_framework.permissions import BasePermission


from rest_framework.permissions import BasePermission
from rest_framework.exceptions import ValidationError


class HasRefreshTokenCookie(BasePermission):

    def has_permission(self, request, view):
        if not request.COOKIES.get("refresh_token"):
            raise ValidationError({"detail": "Refresh-Token required."}, code=400)
        return True
