from rest_framework.permissions import SAFE_METHODS, BasePermission

from ..utils import READ_ONLY_MESSAGE


class ReadOnly(BasePermission):
    message = READ_ONLY_MESSAGE

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
