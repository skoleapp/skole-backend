from django.contrib.auth import get_user_model
from rest_framework import serializers
from .password_serializer import PasswordSerializer


class UserSerializer(serializers.ModelSerializer):
    password = PasswordSerializer(write_only=True)

    class Meta:
        model = get_user_model()

        fields = [
            "bio",
            "email",
            "password",
            "points",
            "title",
            "username",
        ]

        read_only_fields = [
            "points",
        ]
