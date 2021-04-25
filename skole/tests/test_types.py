from __future__ import annotations

from django.http import HttpRequest
from graphql import GraphQLField, GraphQLObjectType, GraphQLScalarType, GraphQLSchema
from graphql.language.ast import OperationDefinition, SelectionSet

from skole.types import ResolveInfo


def test_resolve_info_init() -> None:
    graphql_object_type = GraphQLObjectType(
        "foo",
        fields={"field": GraphQLField(GraphQLScalarType("bar", serialize=lambda x: x))},
    )
    info = ResolveInfo(
        field_name="",
        field_asts=[],
        return_type=graphql_object_type,
        parent_type=graphql_object_type,
        schema=GraphQLSchema(graphql_object_type),
        fragments={},
        root_value=None,
        operation=OperationDefinition("", SelectionSet(None)),
        variable_values={},
        context=HttpRequest(),
        path=None,
    )
    assert hasattr(info, "field_name")
    assert hasattr(info, "field_asts")
    assert hasattr(info, "return_type")
    assert hasattr(info, "parent_type")
    assert hasattr(info, "schema")
    assert hasattr(info, "fragments")
    assert hasattr(info, "root_value")
    assert hasattr(info, "operation")
    assert hasattr(info, "variable_values")
    assert hasattr(info, "context")
    assert hasattr(info, "path")
