import datetime
import functools
import hashlib
import importlib
import inspect
import json
import re
from collections.abc import Collection, Generator
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Optional, TypeVar, Union, cast

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.test import TestCase
from django.utils.translation import get_language
from graphql_jwt.settings import jwt_settings
from graphql_jwt.shortcuts import get_token
from graphql_jwt.utils import delete_cookie

from skole.models import User
from skole.types import ID, AnyJson, JsonDict

FileData = Optional[Collection[tuple[str, File]]]

# Files that exist in the repo for testing.
TEST_ATTACHMENT_PNG = "media/uploads/attachments/test_attachment.png"
TEST_AVATAR_JPG = "media/uploads/avatars/test_avatar.jpg"
TEST_RESOURCE_PDF = "media/uploads/resources/test_resource.pdf"

# Example filepaths that uploaded files will get after their names get anonymized.
# Meant to be used with `is_slug_match()`.
UPLOADED_ATTACHMENT_PNG = "media/uploads/attachments/attachment.png"
UPLOADED_AVATAR_JPG = "media/uploads/avatars/avatar.jpg"
UPLOADED_RESOURCE_PDF = "media/uploads/resources/resource.pdf"

json_encode = functools.partial(json.dumps, cls=DjangoJSONEncoder)


class SkoleSchemaTestCase(TestCase):
    """
    Base class for all schema tests.

    Heavily inspired by `graphene_utils.testing.GraphQLTestCase`.

    Attributes:
        authenticated_user: When set to an ID, a JWT token made for the
            user with this pk is sent with all the requests.
    """

    fixtures = ["test-data.yaml"]

    authenticated_user: ID = None

    def query(
        self,
        query: str,
        op_name: Optional[str] = None,
        input_data: Optional[JsonDict] = None,
        variables: Optional[JsonDict] = None,
        headers: Optional[JsonDict] = None,
        file_data: FileData = None,
    ) -> HttpResponse:
        """
        Overridden to allow uploading files with a multipart/form-data POST.

        This should probably not be used on its own, but instead should be called
        through `self.execute` or `self.execute_input_mutation` etc.

        Args:
            query: GraphQL query to run.
            op_name: If the query is a mutation or named query, you must
                supply the op_name.  For anon queries ("{ ... }"),
                should be None (default).
            input_data: If provided, the $input variable in GraphQL will be set
                to this value. If both ``input_data`` and ``variables``,
                are provided, the ``input`` field in the ``variables``
                dict will be overwritten with this value.
            variables: If provided, the "variables" field in GraphQL will be
                set to this value.
            headers: If provided, the headers in POST request to GRAPHQL_URL
                will be set to this value.
            file_data: Files to the mutation as a sequence of (field_name, file) pairs.
                By passing these the self.query() will automatically use the correct
                multipart/form-data content-type. It will also automatically handle all
                of the inserting of the files into the request body.

        Returns:
            Response object from the client.
        """
        body: JsonDict = {"query": query}
        if op_name:
            body["operation_name"] = op_name
        if variables:
            body["variables"] = variables
        if input_data:
            if variables in body:
                body["variables"]["input"] = input_data
            else:
                body["variables"] = {"input": input_data}

        extra = headers or {}

        if file_data:
            # This imitates the way Apollo Client places files in a GraphQL query.
            variable_map = {}
            file_dict = {}
            for i, (field, file) in enumerate(file_data, start=1):
                variable_map[str(i)] = [f"variables.input.{field}"]
                file_dict[str(i)] = file

            data: Union[JsonDict, str] = {
                "operations": json_encode(body),
                "map": json_encode(variable_map),
                **file_dict,
            }

        else:
            data = json_encode(body)
            extra.update({"content_type": "application/json"})

        return self.client.post(
            path="/graphql/",
            data=data,
            **extra,
            HTTP_ACCEPT_LANGUAGE=get_language(),
        )

    def execute(
        self, graphql: str, *, assert_error: bool = False, **kwargs: Any
    ) -> Any:
        """
        Run a GraphQL query, if `assert_error` parameter is False assert that status
        code was 200 (=syntax was ok) and that the result didn't have "error" section.
        If `assert_error` is True, we assert that the result does contain "error".

        Args:
            graphql: The query that will be executed.
            assert_error: Can be set to True for making that execution pass when
                the request fails and the response has a top level "errors" section.
                Note that when form mutations error out, they don't have this section.
            **kwargs: `header` kwarg will get merged with the possible token header.
                Other kwargs are passed straight to self.query, see also its docstring.

        Returns:
            The resulting JSON data.name section if `assert_error` is False.
            Otherwise returns both the "error" and "data" sections.

            Note: The return value is type hinted for simplicity to be a `Any`,
            so that the callers never need to do any casting.
            In reality this can return either a `JsonDict` or a `list[JsonDict]`.
        """

        if self.authenticated_user:
            token = get_token(get_user_model().objects.get(pk=self.authenticated_user))
            headers = {"HTTP_AUTHORIZATION": f"JWT {token}"}
        else:
            headers = {}

        headers.update(kwargs.pop("headers", {}))

        response = self.query(graphql, **kwargs, headers=headers)

        if not self.authenticated_user:
            delete_cookie(response, jwt_settings.JWT_COOKIE_NAME)

        if assert_error:
            self._assert_response_has_errors(response)
            return json.loads(response.content)
        else:
            self._assert_response_no_errors(response)
            data = json.loads(response.content)["data"]
            assert len(data) == 1, "This method only returns data from the first key."
            return data.popitem()[1]

    def execute_input_mutation(
        self,
        *,
        name: str,
        input_type: str,
        input: JsonDict,
        result: str,
        fragment: str = "",
        file_data: FileData = None,
        assert_error: bool = False,
    ) -> JsonDict:
        """
        Shortcut for running a mutation which takes only an input argument.

        Args:
            input_type: Name of the GraphQL input type object.
            name: Name of the mutation in the schema.
            input: The arguments going into the input argument of the mutation.
            result: GraphQL snippet of the fields which want to be queried from the result.
            fragment: Extra GraphQL snippet which will be inserted before the mutation query.
                Useful for providing a GraphQL fragment which can then used in `result.`
            file_data: Files to the mutation as a sequence of (field_name, file) pairs.
                By passing these the self.query() will automatically use the correct
                multipart/form-data content-type. It will also automatically handle all
                of the inserting of the files into the request body.
            assert_error: Whether the result should contain a top level "errors" section.
                Form mutation errors never have this.

        Returns:
            The resulting JSON data.name section if `assert_error` is False.
            Otherwise returns both the "error" and "data" sections.
        """
        graphql = (
            fragment
            + f"""
            mutation ($input: {input_type}) {{
                {name}(input: $input) {{
                    errors {{
                        field
                        messages
                    }}
                    {result}
                }}
            }}
            """
        )
        return self.execute(
            graphql=graphql,
            input_data=input,
            file_data=file_data,
            assert_error=assert_error,
        )

    def execute_non_input_mutation(
        self, *, name: str, result: str, fragment: str = "", assert_error: bool = False
    ) -> JsonDict:
        """
        Shortcut for running a mutation which takes no input as an argument.

        Args:
            name: Name of the mutation in the schema.
            result: GraphQL snippet of the fields which want to be queried from the result.
            fragment: Extra GraphQL snippet which will be inserted before the mutation query.
                Useful for providing a GraphQL fragment which can then used in `result.`
            assert_error: Whether the result should contain a top level "errors" section.
                Form mutation errors never have this.

        Returns:
            The resulting JSON data.name section if `assert_error` is False.
            Otherwise returns both the "error" and "data" sections.
        """

        graphql = (
            fragment
            + f"""
            mutation {{
                {name} {{
                    errors {{
                        field
                        messages
                    }}
                    {result}
                }}
            }}
            """
        )
        return self.execute(graphql=graphql, op_name=name, assert_error=assert_error)

    def assert_field_fragment_matches_schema(self, field_fragment: str, /) -> None:
        """
        Assert the validity of the given field fragment.

        This validates that the fragment contains all of the fields that are actually
        queryable on that object type it was defined for.
        """
        # language=GraphQL
        graphql = """
            query IntrospectAllFields($name: String!) {
                __type(name: $name) {
                    fields {
                        name
                    }
                }
            }
            """
        object_type = field_fragment.split()[3]
        res = self.execute(graphql, variables={"name": object_type})

        for field in res["fields"]:
            self.assertIn(field["name"], field_fragment)

    def get_authenticated_user(self) -> User:
        """
        Return the currently authenticated user.

        Raises:
            ValueError: If `self.authenticated_user` was `None`.
        """
        if self.authenticated_user is None:
            raise ValueError("Can't call if `self.authenticated_user` is `None`.")
        return get_user_model().objects.get(pk=self.authenticated_user)

    def _assert_response_no_errors(self, response: HttpResponse) -> None:
        content = json.loads(response.content)
        self.assertNotIn("errors", content)
        assert response.status_code == 200

    def _assert_response_has_errors(self, response: HttpResponse) -> None:
        content = json.loads(response.content)
        self.assertIn("errors", content)
        if "data" in content and content["data"]:
            # If there is a "data" dict it should only have keys with empty values.
            for key, value in content["data"].items():
                assert isinstance(key, str)
                assert value is None


def get_form_error(res: AnyJson, /) -> str:
    """Return the first error message from a result containing a form mutation error."""
    try:
        # Ignore: It's fine if `res` is a `list[JsonDict]` and this raises an error.
        return res["errors"][0]["messages"][0]  # type: ignore[call-overload]
    except (IndexError, KeyError, TypeError):
        raise AssertionError(
            f"`res` didn't contain a form mutation error: \n{res}"
        ) from None


def get_graphql_error(res: AnyJson, /) -> str:
    """Return the first error message from a result containing a GraphQL error."""
    try:
        # Ignore: It's fine if `res` is a `list[JsonDict]` and this raises an error.
        return res["errors"][0]["message"]  # type: ignore[call-overload]
    except (IndexError, KeyError, TypeError):
        raise AssertionError(f"`res` didn't contain a GraphQL error: \n{res}") from None


def is_iso_datetime(datetime_string: str, /) -> bool:
    """
    Return True if the given string is a valid ISO-format datetime, otherwise False.

    Examples:
        >>> is_iso_datetime("2020-01-01T12:00:00+00:00")
        True
        >>> is_iso_datetime("2020-01-01")
        False
        >>> is_iso_datetime("T12:00:00+00:00")
        False
        >>> is_iso_datetime("foobar")
        False
    """
    try:
        datetime.datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S%z")
    except ValueError:
        return False
    else:
        return True


def is_slug_match(file_path: str, url_with_slug: str) -> bool:
    """
    Return True if the two paths match each other with an optional slug.

    The paths will still match even if one of them is a relative path, and the other
    is an absolute one (no prexix slash).

    Examples:
        >>> is_slug_match("/media/test/foo.jpg", "/media/test/fooXfa123.jpg")
        True
        >>> is_slug_match("/media/test/foo.jpg", "/media/test/foo.jpg")
        True
        >>> is_slug_match("media/test/foo.jpg", "/media/test/foo.jpg")
        True
        >>> is_slug_match("/media/test/foo.jpg", "/media/test/foo-bar.jpg")
        False
        >>> is_slug_match("/media/test/foo.jpg", "/foo.jpg")
        False
    """
    path, extension = file_path.removeprefix("/").rsplit(".", 1)
    return bool(re.match(fr"^/{path}\w*\.{extension}$", url_with_slug))


def checksum(obj: Any) -> str:
    """
    Return a stable 20 digit hex checksum for the given object based on its source code.

    Useful for testing if a source code of the object has changed.
    For objects wrapped with `@wraps` or `update_wrapper`, this returns an hash for the
    *original* object's source code, since `inspect.getsource` always "unwraps" the
    object before finding the source.

    Does not work with builtin objects, or others where `getsource` doens't work.

    Examples:
        >>> def foo(): pass
        >>> checksum(foo)
        'f5895e0ae9566948c330'
    """
    return hashlib.shake_256(  # pylint: disable=too-many-function-args
        inspect.getsource(obj).encode()
    ).hexdigest(10)


@contextmanager
def open_as_file(path: Union[str, Path]) -> Generator[File, None, None]:
    """Use as a contextmanager to open the file in the given path as a Django `File`."""
    if not isinstance(path, Path):
        path = Path(path)

    with open(settings.BASE_DIR / path, "rb") as f:
        yield File(f)


def get_token_from_email(body: str) -> str:
    """
    Return the token from an email body that has an URL with a token query param.

    Returns an empty string if no token was found.

    Examples:
        >>> get_token_from_email("https://foo.com/?token=secret")
        'secret'
        >>> get_token_from_email("Hello user www.foo.com?token=secret bye!")
        'secret'
        >>> get_token_from_email("Hello https://foo.com/ dude.")
        ''
        >>> get_token_from_email("")
        ''
    """
    match = re.search(r"\?token=(\S*)", body)
    return match.group(1) if match else ""


M = TypeVar("M", bound=ModuleType)


@contextmanager
def reload_module(module: M) -> Generator[Callable[[], M], None, None]:
    """
    Use as a context manager to reload the module at the end of the block.

    Yields:
        A function that can be called without any arguments to reload `module`.
    """
    try:
        # The cast is required because `partial` removes argument type information:
        # https://github.com/python/mypy/issues/1484
        yield cast(Callable[[], M], functools.partial(importlib.reload, module))
    finally:
        importlib.reload(module)
