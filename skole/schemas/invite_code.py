from skole.models import InviteCode
from skole.schemas.base import SkoleDjangoObjectType


class InviteCodeObjectType(SkoleDjangoObjectType):
    class Meta:
        model = InviteCode
        fields = ("code", "usages")
