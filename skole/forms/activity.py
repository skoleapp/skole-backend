from skole.forms.base import SkoleUpdateModelForm
from skole.models import Activity


class MarkActivityAsReadForm(SkoleUpdateModelForm):
    class Meta:
        model = Activity
        fields = ("id", "read")
