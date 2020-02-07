from django import forms

from app.models.course import Course


class CreateCourseForm(forms.ModelForm):
    subject_id = forms.IntegerField(required=False)
    school_id = forms.IntegerField()

    class Meta:
        model = Course
        fields = ("name", "code", "subject_id", "school_id")
