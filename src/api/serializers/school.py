from rest_framework import serializers

from core.models import School


class SchoolSerializer(serializers.ModelSerializer):
    school_type = serializers.CharField(source='get_school_type_display')

    class Meta:
        model = School
        fields = ("id", "school_type", "name", "city", "country")
        read_only_fields = fields
