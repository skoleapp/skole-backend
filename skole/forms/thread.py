from skole.forms.base import SkoleModelForm, SkoleUpdateModelForm
from skole.models import Thread


class CreateThreadForm(SkoleModelForm):
    class Meta:
        model = Thread
        fields = ("title", "text", "image", "user")

    def save(self, commit: bool = True) -> Thread:
        assert self.request is not None
        # Should always be authenticated here, so fine to raise ValueError here
        # if we accidentally assign anonymous user to the user.
        self.instance.user = self.request.user
        return super().save()


class DeleteThreadForm(SkoleUpdateModelForm):
    class Meta:
        model = Thread
        fields = ("id",)
