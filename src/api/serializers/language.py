from rest_framework import serializers
from core.utils import LANGUAGES


class LanguageSerializer(serializers.Serializer):
    language = serializers.ChoiceField(choices=LANGUAGES)

    class Meta:
        fields = ["language"]
