from api.utils.common import TargetForm
from app.utils.dummy_model import DummyModel


class DeleteObjectForm(TargetForm):
    class Meta:
        model = DummyModel
        fields = ("comment_id", "resource_id", "resource_part_id", "vote_id")
