from typing import List

from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from rest_framework import permissions, request, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from ..permissions import IsAnonymous, IsSelfOrAdminReadOnly, ReadOnly
from ..serializers import (
    AuthTokenSerializer,
    RegisterSerializer,
    UserDetailSerializer,
    UserSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()
    search_fields = ["username"]

    def get_serializer_class(self) -> BaseSerializer:
        if self.action in {"retrieve", "update", "delete"}:
            return UserDetailSerializer

        elif self.action == "register":
            return RegisterSerializer

        elif self.action == "login":
            return AuthTokenSerializer

        else:
            return self.serializer_class

    def get_permissions(self) -> List[BasePermission]:
        if self.action in {"list", "create"}:
            permission_classes = [permissions.IsAuthenticated, ReadOnly]

        elif self.action in {"register", "login"}:
            permission_classes = [IsAnonymous]

        else:
            permission_classes = [IsSelfOrAdminReadOnly]

        return [permission() for permission in permission_classes]

    def get_queryset(self) -> QuerySet:
        """Allow superuser to view all users."""
        if self.action == "list":

            if self.request.user.is_superuser:
                return self.queryset

            else:
                return self.queryset.none()

        elif self.action in {"vendor_profile", "set_profile_image", "set_languages"}:
            return self.queryset.filter(is_vendor=True)

        else:
            return self.queryset

    def get_object(self):
        if self.kwargs.get("pk", None) == "me":
            self.kwargs["pk"] = self.request.user.pk

        return super().get_object()

    @action(detail=False, methods=["POST"], url_path="register")
    def register(self, request: request) -> Response:
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status.HTTP_200_OK)

        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["POST"], url_path="login")
    def login(self, request: request) -> Response:
        serializer = self.get_serializer(data=request.data, context={"request": request})

        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})