from skole.models import Author
from skole.schemas.base import SkoleDjangoObjectType


class AuthorObjectType(SkoleDjangoObjectType):
    class Meta:
        model = Author
        fields = ("id", "name", "user")
