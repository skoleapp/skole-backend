
from typing import Dict

from core.models import User
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from core.utils import JsonDict
from ..utils import (OLD_PASSWORD_NOT_CORRECT_MESSAGE,
                     PASSWORDS_DO_NOT_MATCH_MESSAGE,
                     UNABLE_TO_AUTHENTICATE_MESSAGE,
                     USER_DOES_NOT_EXIST_MESSAGE)


class AuthTokenSerializer(serializers.Serializer):
    username_or_email = serializers.CharField()
    password = serializers.CharField(style={"input_type": "password"}, trim_whitespace=False)

    def validate(self, attrs: JsonDict) -> JsonDict:
        username_or_email = attrs.get("username_or_email")
        password = attrs.get("password")

        if "@" in username_or_email:
            kwargs = {"email": username_or_email}
        else:
            kwargs = {"username": username_or_email}
        try:
            user = get_user_model().objects.get(**kwargs)

            user = authenticate(
                request=self.context.get("request"), username=user.username, password=password
            )

            if not user:
                msg = UNABLE_TO_AUTHENTICATE_MESSAGE
                raise serializers.ValidationError(msg, code="authentication")

            attrs["user"] = user
            return attrs

        except get_user_model().DoesNotExist:
            msg = USER_DOES_NOT_EXIST_MESSAGE
            raise serializers.ValidationError(msg, code="authentication")


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        write_only=True, min_length=6, style={"input_type": "password", "placeholder": "Password"}
    )

    confirm_password = serializers.CharField(
        write_only=True, style={"input_type": "password", "placeholder": "Password"}
    )

    class Meta:
        fields = ["password", "confirm_password"]

    def validate(self, data: JsonDict) -> JsonDict:
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(PASSWORDS_DO_NOT_MATCH_MESSAGE)

        return data


class ChangePasswordSerializer(PasswordSerializer):
    old_password = serializers.CharField(
        write_only=True, style={"input_type": "password", "placeholder": "Password"}
    )

    class Meta(PasswordSerializer.Meta):
        fields = ["old_password", "password", "confirm_password"]

    def validate(self, data: JsonDict) -> JsonDict:
        old_password = data["old_password"]
        request = self.context.get("request")

        if not request.user.check_password(old_password):
            raise serializers.ValidationError(OLD_PASSWORD_NOT_CORRECT_MESSAGE)

        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(PASSWORDS_DO_NOT_MATCH_MESSAGE)

        return data

