from graphene_django.utils import GraphQLTestCase
from mypy.types import JsonDict


def query_schools(test_cls: GraphQLTestCase) -> JsonDict:
    query = """
        query {
          schools {
            id
            name
            schoolType
            city
          }
        }
        """

    return test_cls.client.execute(query)


def query_school(test_cls: GraphQLTestCase, id: int = 1) -> JsonDict:
    variables = {"id": id}

    query = """
        query school($id: ID!) {
          school(id: $id) {
            id
            name
            schoolType
            city
          }
        }
        """

    return test_cls.client.execute(query, variables=variables)


def query_school_types(test_cls: GraphQLTestCase) -> JsonDict:
    query = """
        query {
          schoolTypes {
            id
            name
          }
        }
        """

    return test_cls.client.execute(query)


def query_school_type(test_cls: GraphQLTestCase, id: int) -> JsonDict:
    variables = {"id": id}

    query = """
        query schoolType($id: ID!) {
          schoolType(id: $id) {
            id
            name
          }
        }
        """

    return test_cls.client.execute(query, variables=variables)
