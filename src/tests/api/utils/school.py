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


def query_school(test_cls: GraphQLTestCase, school_id: int = 1) -> JsonDict:
    variables = {"schoolId": school_id}

    query = """
        query school($schoolId: Int!) {
          school(schoolId: $schoolId) {
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


def query_school_type(test_cls: GraphQLTestCase, school_type_id: int) -> JsonDict:
    variables = {"schoolTypeId": school_type_id}

    query = """
        query schoolType($schoolTypeId: Int!) {
          schoolType(schoolTypeId: $schoolTypeId) {
            id
            name
          }
        }
        """

    return test_cls.client.execute(query, variables=variables)
