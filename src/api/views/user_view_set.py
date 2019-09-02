from rest_framework import viewsets
from ..serializers import UserSerializer
from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets

from ..serializers import UserDetailSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()
    search_fields = ["username"]

