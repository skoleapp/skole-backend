from skole.models import Activity

from .base import SkoleUpdateModelForm


class MarkActivityReadForm(SkoleUpdateModelForm):
    class Meta:
        model = Activity
        fields = ("id", "read")
