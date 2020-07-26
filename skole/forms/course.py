from django import forms

from skole.models import Course
from skole.utils.forms import DeleteObjectForm


class CreateCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ("name", "code", "subjects", "school")


class DeleteCourseForm(DeleteObjectForm):
    class Meta(DeleteObjectForm.Meta):
        model = Course
