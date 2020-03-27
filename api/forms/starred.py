from api.utils.forms import TargetForm
from core.models import Starred


class StarForm(TargetForm):
    class Meta:
        model = Starred
        fields = (
            "course",
            "resource",
        )
