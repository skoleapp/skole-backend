from api.utils.common import TargetForm
from app.models import Vote


class CreateVoteForm(TargetForm):
    class Meta:
        model = Vote
        fields = (
            "status",
            "comment",
            "course",
            "resource",
        )
