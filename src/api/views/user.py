from typing import List, Any, Union, Tuple

from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from rest_framework import permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework import mixins

from api.serializers import UserPrivateDetailSerializer
from ..permissions import IsAnonymous, IsOwnerOrReadOnly
from ..serializers import (
    AuthTokenSerializer,
    ChangePasswordSerializer,
    RegisterSerializer,
    UserPublicDetailSerializer,
    UserSerializer,
)
from ..utils import (
    AUTHENTICATION_FAILED_MESSAGE,
    LANGUAGE_SET_SUCCESSFULLY_MESSAGE,
    PASSWORD_SET_SUCCESSFULLY_MESSAGE,
    USER_REGISTERED_SUCCESSFULLY_MESSAGE,
)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()
    search_fields = ["username"]
    permission_classes = (IsOwnerOrReadOnly,)

    def get_serializer_class(self) -> Union[BaseSerializer, Any]:
        if self.action in {"retrieve", "partial_update", "update", "delete"}:
            if self.get_object().pk == self.request.user.pk:
                return UserPrivateDetailSerializer
            else:
                return UserPublicDetailSerializer

        elif self.action == "register":
            return RegisterSerializer

        elif self.action == "login":
            return AuthTokenSerializer

        elif self.action == "change_password":
            return ChangePasswordSerializer

        else:
            return self.serializer_class

    def get_permissions(self) -> Tuple:
        if self.action == "list":
            permission_classes = (permissions.AllowAny,)

        elif self.action in {"retrieve", "partial_update", "update", "destroy"}:
            permission_classes = (IsOwnerOrReadOnly,)

        elif self.action in {"register", "login"}:
            permission_classes = (IsAnonymous,)

        elif self.action in {"change_password", "refresh_token"}:
            permission_classes = (permissions.IsAuthenticated,)

        else:
            permission_classes = self.permission_classes

        return tuple(permission() for permission in permission_classes)

    def get_object(self):
        if self.kwargs.get("pk", None) == "me":
            self.kwargs["pk"] = self.request.user.pk
        return super().get_object()

    @action(detail=False, methods=["POST"], url_path="register")
    def register(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                data={"message": USER_REGISTERED_SUCCESSFULLY_MESSAGE},
                status=status.HTTP_201_CREATED,
            )

        else:
            return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["POST"], url_path="login")
    def login(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token, created = Token.objects.get_or_create(user=user)

            if not created:
                token = get_user_model().objects.refresh_token(user=user, token=token)

            return Response(data={"token": token.key}, status=status.HTTP_200_OK)

        return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["GET"], url_path="refresh-token")
    def refresh_token(self, request: Request) -> Response:
        try:
            token = Token.objects.get(user=request.user)
            refresh_token = get_user_model().objects.refresh_token(user=request.user, token=token)

        except Token.DoesNotExist:
            return Response(
                data={"error": AUTHENTICATION_FAILED_MESSAGE}, status=status.HTTP_401_UNAUTHORIZED
            )

        return Response(data={"refresh_token": refresh_token.key}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["POST"], url_path="change-password")
    def change_password(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            get_user_model().objects.set_password(
                user=request.user, password=serializer.validated_data["password"]
            )
            return Response(
                data={"message": PASSWORD_SET_SUCCESSFULLY_MESSAGE}, status=status.HTTP_200_OK
            )

        return Response(data={"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

