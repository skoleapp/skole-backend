"""
Module for testing compatibility of patched or overridden 3rd party code.

Theses tests that make sure that we immediately notice if the source code
of the functions we have overridden or monkey value has changed,
so that we can always ensure full compatibility.

If any of these tests fail, it's not the end of the world, one just needs to check
the releases of that package and see what has changed in the code. After verifying
that the change didn't affect our usage, or after altering our overridden code, the
checksum in the assertion can be changed to correspond to the new 3rd party code.
"""
import graphql.execution.utils
import graphql_jwt.utils
from graphene_django.views import GraphQLView

from skole.tests.helpers import checksum


def test_report_error_code_has_not_changed() -> None:
    assert (
        checksum(graphql.execution.utils.ExecutionContext.report_error)
        == "fa7cdbca837c4ebfd294"
    )


def test_set_cookie_has_not_changed() -> None:
    assert checksum(graphql_jwt.utils.set_cookie) == "b167f632dda778326506"


def test_graphql_view_code_has_not_changed() -> None:
    assert checksum(GraphQLView.parse_body) == "b6d13668aa8a9c22e9a2"


def test_graphql_resolve_info_code_has_not_changed() -> None:
    assert checksum(graphql.ResolveInfo) == "d7d63b1a17fda05e4629"
