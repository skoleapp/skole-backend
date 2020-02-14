from django.contrib import admin
from django.contrib.auth import get_user_model

from app.models import (
    City,
    Country,
    Course,
    Resource,
    ResourcePart,
    ResourceType,
    School,
    SchoolType,
)

admin.site.register(City)
admin.site.register(Country)
admin.site.register(Course)
admin.site.register(Resource)
admin.site.register(ResourceType)
admin.site.register(ResourcePart)
admin.site.register(School)
admin.site.register(SchoolType)
admin.site.register(get_user_model())
