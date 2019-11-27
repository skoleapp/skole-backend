from django import forms
from app.models.course import Course


class CreateCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ("name", "code", "subject", "school")
