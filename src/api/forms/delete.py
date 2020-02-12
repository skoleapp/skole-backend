from api.utils.common import TargetForm
from app.utils.delete_object_model import DeleteObjectModel


class DeleteObjectForm(TargetForm):
    class Meta:
        model = DeleteObjectModel
        fields = "__all__"
