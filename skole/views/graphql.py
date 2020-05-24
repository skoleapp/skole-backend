import json
from typing import Union

from django.http import HttpRequest, QueryDict
from graphene_django.views import GraphQLView
from mypy.types import JsonDict


class SkoleGraphQLView(GraphQLView):
    """This view should be used as the graphql endpoint of the app."""

    def parse_body(self, request: HttpRequest) -> Union[JsonDict, QueryDict]:
        """The difference to the original `parse_body` is that we can upload files.

        Source: https://github.com/lmcgartland/graphene-file-upload/blob/master/graphene_file_upload/django/__init__.py
        """
        content_type = self.get_content_type(request)

        if content_type == "multipart/form-data":
            operations = json.loads(request.POST["operations"])
            files_map = json.loads(request.POST["map"])
            return _place_files_in_operations(operations, files_map, request.FILES)
        else:
            return super().parse_body(request)


# Ignore: The types of the parameters and return values are too complex
#  to type-annotate reasonably. Since these are one-off functions it's fine.
def _place_files_in_operations(operations, files_map, files):  # type: ignore[no-untyped-def]
    # operations: dict or list
    # files_map: {filename: [path, path, ...]}
    # files: {filename: FileStorage}

    for key, values in files_map.items():
        for val in values:
            path = val.split(".")
            operations = _place_file_in_operations(operations, path, files[key])

    return operations


# Ignore: Same as above.
def _place_file_in_operations(ops, path, obj):  # type: ignore[no-untyped-def]
    if len(path) == 0:
        return obj

    if isinstance(ops, list):
        key = int(path[0])
        sub = _place_file_in_operations(ops[key], path[1:], obj)
        return [*ops[:key], sub, *ops[key + 1 :]]

    if isinstance(ops, dict):
        key = path[0]
        sub = _place_file_in_operations(ops[key], path[1:], obj)
        return {**ops, key: sub}

    raise TypeError("Expected ops to be list or dict.")
