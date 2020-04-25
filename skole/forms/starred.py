from skole.models import Starred
from skole.utils.forms import TargetForm


class StarForm(TargetForm):
    class Meta:
        model = Starred
        fields = (
            "course",
            "resource",
        )
