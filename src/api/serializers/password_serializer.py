from rest_framework import serializers


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
