from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers


class AuthTokenSerializer(serializers.Serializer):
    username_or_password = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        username_or_password = attrs.get('username_or_password')
        password = attrs.get('password')

        if '@' in username_or_password:
            kwargs = {'email': username_or_password}
        else:
            kwargs = {'username': username_or_password}
        try:
            user = get_user_model().objects.get(**kwargs)

            user = authenticate(
                request=self.context.get('request'),
                username=user.username,
                password=password
            )

            if not user:
                msg = ('Unable to authenticate with provided credentials.')
                raise serializers.ValidationError(msg, code='authentication')

            attrs['user'] = user
            return attrs
        
        except get_user_model().DoesNotExist:
            msg = ('A user with the provided username or email address does not exist.')
            raise serializers.ValidationError(msg, code='authentication')


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        write_only=True,
        min_length=6,
        style={'input_type': 'password', 'placeholder': 'Password'}
    )

    confirm_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password', 'placeholder': 'Password'}
    )

    class Meta:
        fields = [
            "password",
            "confirm_password"
        ]

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")

        return data["password"]
