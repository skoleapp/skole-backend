from rest_framework import request
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.viewsets import ModelViewSet

from ..utils import READ_ONLY_MESSAGE


class ReadOnly(BasePermission):
    message = READ_ONLY_MESSAGE

    def has_permission(self, request: request, view: ModelViewSet) -> bool:
        return request.method in SAFE_METHODS
