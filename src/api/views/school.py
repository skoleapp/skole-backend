from rest_framework import viewsets
from rest_framework import mixins

from api.permissions import ReadOnly
from api.serializers import SchoolSerializer
from core.models import School


class SchoolViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin,
                    mixins.RetrieveModelMixin):
    serializer_class = SchoolSerializer
    queryset = School.objects.all().order_by("name")
    search_fields = ["name"]
    permission_classes = (ReadOnly,)

    def get_queryset(self):
        queryset = self.queryset
        school_type = self.request.query_params.get("school_type", None)
        if school_type is not None:
            school_type = school_type.upper().replace("-", "_")
            queryset = queryset.filter(school_type=school_type)
        return queryset
