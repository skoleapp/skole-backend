from typing import Dict

from typing import Dict
from core.models import User
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .auth import PasswordSerializer


class UserSerializer(serializers.ModelSerializer):
    password = PasswordSerializer(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ["id", "email", "username", "title", "bio", "points", "password"]
        read_only_fields = ["points"]


class UserDetailSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ["id", "email", "username", "title", "bio", "points"]

    def update(self, instance: User, validated_data: Dict[str, str]) -> User:
        return get_user_model().objects.update_user(instance, **validated_data)
