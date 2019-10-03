from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "title", "bio", "points")
        read_only_fields = fields


class UserPublicDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "title", "bio", "points")
        read_only_fields = ("id", "points")


class UserPrivateDetailSerializer(UserPublicDetailSerializer):
    class Meta(UserPublicDetailSerializer.Meta):
        fields = ("id", "email", "username", "title", "bio", "points", "language")
