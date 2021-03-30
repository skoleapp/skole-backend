from skole.models import ReferralCode
from skole.schemas.base import SkoleDjangoObjectType


class ReferralCodeObjectType(SkoleDjangoObjectType):
    class Meta:
        model = ReferralCode
        fields = ("code", "usages")
