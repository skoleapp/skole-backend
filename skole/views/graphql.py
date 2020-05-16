import json
from typing import Optional, Tuple, Union

from django.http import HttpRequest, QueryDict
from django.http.response import HttpResponseBadRequest
from django.utils.translation import gettext as _
from graphene_django.views import GraphQLView, HttpError
from mypy.types import JsonDict


class CustomGraphQLView(GraphQLView):
    """This view should be used as the graphql endpoint of the app."""

    def parse_body(self, request: HttpRequest) -> Union[JsonDict, QueryDict]:
        """The difference to the original `parse_body` is that we can upload files.

        Source: https://stackoverflow.com/a/58059674
        """
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

    def get_response(self, request, data, show_graphiql=False):
        """Just like the normal `get_response`, but overridden to block mutations from superusers."""
        query, variables, operation_name, id = self.get_graphql_params(request, data)

        # Only changed thing in this method.
        if request.user.is_superuser:
            return self.superuser_error(request, operation_name, show_graphiql)

        execution_result = self.execute_graphql_request(
            request, data, query, variables, operation_name, show_graphiql
        )

        status_code = 200
        if execution_result:
            response = {}

            if execution_result.errors:
                response["errors"] = [
                    self.format_error(e) for e in execution_result.errors
                ]

            if execution_result.invalid:
                status_code = 400
            else:
                response["data"] = execution_result.data

            if self.batch:
                response["id"] = id
                response["status"] = status_code

            result = self.json_encode(request, response, pretty=show_graphiql)
        else:
            result = None

        return result, status_code

    def superuser_error(
        self, request: HttpRequest, operation_name: Optional[str], show_graphiql: bool
    ) -> Tuple[str, int]:
        message = _("Cannot perform GraphQL queries as a superuser.")
        if operation_name:
            # The query was a mutation.

            # `operation_name` is somehow PascalCased even though the mutation names
            # that frontend is expecting to use to access the result are camelCased.
            op_name_camelcase = operation_name[0].lower() + operation_name[1:]
            response = {
                "data": {
                    op_name_camelcase: {
                        "errors": [{"field": "__all__", "messages": [message]}],
                    }
                }
            }
        else:
            # The query was a query.
            response = {
                "errors": [{"messages": [message]}],
            }
        return self.json_encode(request, response, pretty=show_graphiql), 200


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
