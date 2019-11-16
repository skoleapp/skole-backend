from django.contrib import admin
from django.contrib.auth import get_user_model

from app.models.city import City
from app.models.country import Country
from app.models.course import Course
from app.models.language import Language
from app.models.resource import Resource
from app.models.resource_type import ResourceType
from app.models.school import School
from app.models.school_type import SchoolType

admin.site.register(City)
admin.site.register(Country)
admin.site.register(Course)
admin.site.register(Language)
admin.site.register(Resource)
admin.site.register(ResourceType)
admin.site.register(School)
admin.site.register(SchoolType)
admin.site.register(get_user_model())
