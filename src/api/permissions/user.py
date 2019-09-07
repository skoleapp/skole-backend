from django.contrib.auth import get_user_model
from rest_framework import request
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.viewsets import ModelViewSet

from ..utils import NOT_ANONYMOUS_MESSAGE, NOT_OWNER_MESSAGE, READ_ONLY_MESSAGE


class IsAnonymous(BasePermission):
    message = NOT_ANONYMOUS_MESSAGE

    def has_permission(self, request: request, view: ModelViewSet) -> bool:
        return request.user.is_anonymous


class IsSelfOrAdminReadOnly(BasePermission):
    message = NOT_OWNER_MESSAGE

    def has_object_permission(
        self, request: request, view: ModelViewSet, obj: get_user_model()
    ) -> bool:
        if request.user.is_superuser:
            if obj.pk == request.user.id:
                return True
            else:
                return request.method in SAFE_METHODS
        else:
            return obj.pk == request.user.id