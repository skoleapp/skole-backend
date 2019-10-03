from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import SchoolViewSet
from .views import UserViewSet

router = DefaultRouter()
router.register("user", UserViewSet, base_name="user")
router.register("school", SchoolViewSet)

urlpatterns = [
    path("", include(router.urls))
]
