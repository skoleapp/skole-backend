from skole.models import Activity

from .base import SkoleUpdateModelForm


class MarkActivityAsReadForm(SkoleUpdateModelForm):
    class Meta:
        model = Activity
        fields = ("id", "read")
