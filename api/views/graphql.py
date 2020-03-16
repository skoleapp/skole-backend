# https://stackoverflow.com/questions/57812673/how-to-upload-files-in-graphql-using-graphene-file-upload-with-apollo-upload-cli/58059674#58059674
import json
from typing import Union

from django.core.handlers.wsgi import WSGIRequest
from django.http import QueryDict
from django.http.response import HttpResponseBadRequest
from graphene_django.views import GraphQLView, HttpError
from mypy.types import JsonDict


class CustomGraphQLView(GraphQLView):
    def parse_body(self, request: WSGIRequest) -> Union[JsonDict, QueryDict]:
        content_type = self.get_content_type(request)

        if content_type == "application/graphql":
            return {"query": request.body.decode()}

        elif content_type == "application/json":
            try:
                body = request.body.decode("utf-8")
            except Exception as e:
                raise HttpError(HttpResponseBadRequest(str(e)))

            try:
                request_json = json.loads(body)
                if self.batch:
                    assert isinstance(request_json, list), (
                        "Batch requests should receive a list, but received {}."
                    ).format(repr(request_json))
                    assert (
                        len(request_json) > 0
                    ), "Received an empty list in the batch request."
                else:
                    assert isinstance(
                        request_json, dict
                    ), "The received data is not a valid JSON query."
                return request_json
            except AssertionError as e:
                raise HttpError(HttpResponseBadRequest(str(e)))
            except (TypeError, ValueError):
                raise HttpError(HttpResponseBadRequest("POST body sent invalid JSON."))

        # Added for graphql file uploads.
        elif content_type == "multipart/form-data":
            operations = json.loads(request.POST["operations"])
            files_map = json.loads(request.POST["map"])
            return _place_files_in_operations(operations, files_map, request.FILES)

        elif content_type in [
            "application/x-www-form-urlencoded",
        ]:
            return request.POST

        return {}


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

    raise TypeError("Expected ops to be list or dict")
