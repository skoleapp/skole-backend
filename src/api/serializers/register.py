from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.serializers import PasswordSerializer
from core.models import User
from core.utils import JsonDict


class RegisterSerializer(serializers.ModelSerializer):
    password = PasswordSerializer(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ("email", "username", "password")

    def create(self, validated_data: JsonDict) -> User:
        password = validated_data.pop("password")["password"]
        return get_user_model().objects.create_user(**validated_data, password=password)
