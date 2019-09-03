from django.contrib.auth import get_user_model
from rest_framework import serializers

from .user import UserSerializer


class RegisterSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = [
            "email",
            "username",
            "password"
        ]


    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)
