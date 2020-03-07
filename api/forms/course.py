from django import forms

from api.utils.forms import DeleteObjectForm
from core.models.course import Course


class CreateCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ("name", "code", "subject", "school")

class DeleteCourseForm(DeleteObjectForm):
    class Meta(DeleteObjectForm.Meta):
        model = Course
