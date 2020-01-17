from app.models.course import Course
from django import forms


class CreateCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ("name", "code", "subject", "school")
