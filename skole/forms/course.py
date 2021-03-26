from skole.forms.base import SkoleModelForm, SkoleUpdateModelForm
from skole.models import Course


class CreateCourseForm(SkoleModelForm):
    class Meta:
        model = Course
        fields = ("name", "codes", "subjects", "school")

    def save(self, commit: bool = True) -> Course:
        assert self.request is not None
        # Should always be authenticated here, so fine to raise ValueError here
        # if we accidentally assign anonymous user to the user.
        self.instance.user = self.request.user
        return super().save()


class DeleteCourseForm(SkoleUpdateModelForm):
    class Meta:
        model = Course
        fields = ("id",)
