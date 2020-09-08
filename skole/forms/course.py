from skole.models import Course

from .base import SkoleModelForm, SkoleUpdateModelForm


class CreateCourseForm(SkoleModelForm):
    class Meta:
        model = Course
        fields = ("name", "code", "subjects", "school")


class DeleteCourseForm(SkoleUpdateModelForm):
    class Meta:
        model = Course
        fields = ("id",)
