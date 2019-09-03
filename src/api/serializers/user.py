from django.contrib.auth import get_user_model
from rest_framework import serializers

from .auth import PasswordSerializer


class UserSerializer(serializers.ModelSerializer):
    password = PasswordSerializer(write_only=True)

    class Meta:
        model = get_user_model()

        fields = [
            "id",
            "email",
            "username",
            "title",
            "bio",
            "points",
            "password",
        ]

        read_only_fields = [
            "points",
        ]


class UserDetailSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = [
            'id',
            'email',
            'username',
            'title',
            'bio',
            'points',
        ]    
