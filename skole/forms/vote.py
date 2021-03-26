from typing import cast

from django import forms

from skole.forms.base import SkoleModelForm
from skole.models import Vote
from skole.types import JsonDict, VotableModel
from skole.utils.constants import ValidationErrors
from skole.utils.validators import validate_single_target


class CreateVoteForm(SkoleModelForm):

    # Without specifying this explicitly the formfield would be a `TypedChoiceField`,
    # which would then map into a GraphQL `String!` type.
    status = forms.IntegerField(required=True)

    class Meta:
        model = Vote
        fields = ("status", "comment", "thread")

    def clean(self) -> JsonDict:
        data = super().clean()
        assert self.request is not None

        target = data["target"] = cast(
            VotableModel, validate_single_target(data, "comment", "thread")
        )

        if target.user and target.user == self.request.user:
            raise forms.ValidationError(ValidationErrors.VOTE_OWN_CONTENT)
        return data
