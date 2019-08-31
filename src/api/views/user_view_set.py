from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets

from ..serializers import UserDetailSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()
    search_fields = ["username"]
    permission_classes = [permissions.AllowAny]


    def get_serializer_class(self):
        if self.action in ["retrieve", "update", "delete"]:
            return UserDetailSerializer
        
        else:
            return self.serializer_class
