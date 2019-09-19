from django.contrib.auth import get_user_model
from rest_framework.request import Request
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.viewsets import ModelViewSet

from api.utils import NOT_ADMIN_MESSAGE
from core.models import User
from ..utils import NOT_ANONYMOUS_MESSAGE, NOT_OWNER_MESSAGE, READ_ONLY_MESSAGE


class IsAnonymous(BasePermission):
    message = NOT_ANONYMOUS_MESSAGE

    def has_permission(self, request: Request, view: ModelViewSet) -> bool:
        return request.user.is_anonymous


class IsOwnerOrReadOnly(BasePermission):
    message = NOT_OWNER_MESSAGE

    def has_object_permission(self, request: Request, view: ModelViewSet, obj: 'User') -> bool:
        if request.method in SAFE_METHODS:
            return True
        else:
            return obj.pk == request.user.pk

    def has_permission(self, request: Request, view: ModelViewSet) -> bool:
        return request.method in SAFE_METHODS
