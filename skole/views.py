import json
from typing import Dict, List, Union, cast

from django.core.files.uploadedfile import UploadedFile
from django.http import HttpRequest, HttpResponse, QueryDict
from django.utils.datastructures import MultiValueDict
from graphene_django.views import GraphQLView

from skole.types import AnyJson, JsonDict


def health_check(request: HttpRequest) -> HttpResponse:
    """
    AWS ELB will poll this periodically as a health check for the app.

    This can have as much logic as possible, any status other than 200 is considered a
    failure.
    """
    return HttpResponse(status=200)


class SkoleGraphQLView(GraphQLView):
    """The GraphQL endpoint of the app."""

    def parse_body(
        self, request: HttpRequest
    ) -> Union[JsonDict, QueryDict, List[JsonDict]]:
        """
        The difference to the obj `parse_body` is that we can upload files.

        Source: https://github.com/lmcgartland/graphene-file-upload/blob/master/graphene_file_upload/django/__init__.py
        """
        content_type = self.get_content_type(request)

        if content_type == "multipart/form-data":
            operations = json.loads(request.POST["operations"])
            files_map = json.loads(request.POST["map"])
            return self._place_files_in_operations(operations, files_map, request.FILES)
        else:
            return super().parse_body(request)

    @staticmethod
    def _place_files_in_operations(
        ops: AnyJson,
        files_map: Dict[str, List[str]],
        files: "MultiValueDict[str, UploadedFile]",
    ) -> AnyJson:
        """Works with the way Apollo client places file uploads in the operations."""

        def place_file_in_ops(
            ops: AnyJson, path: List[str], file: UploadedFile
        ) -> Union[AnyJson, UploadedFile]:
            if len(path) == 0:
                return file
            if isinstance(ops, list):
                idx = int(path[0])
                return [
                    *ops[:idx],
                    cast(JsonDict, place_file_in_ops(ops[idx], path[1:], file)),
                    *ops[idx + 1 :],
                ]
            if isinstance(ops, dict):
                key = path[0]
                return {**ops, key: place_file_in_ops(ops[key], path[1:], file)}
            raise TypeError(f"Expected `ops` to be a list or a dict, was: {type(ops)}.")

        for key, values in files_map.items():
            for value in values:
                path = value.split(".")
                ops = cast(AnyJson, place_file_in_ops(ops, path, files[key]))

        return ops
