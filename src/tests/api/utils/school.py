from mypy.types import JsonDict

from graphene_django.utils import GraphQLTestCase


def query_schools(test_cls: GraphQLTestCase) -> JsonDict:
    query = """
        query {
          schools {
            id
            name
            schoolType
            city
            country
            subjectCount
            courseCount
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
            country
            subjectCount
            courseCount
          }
        }
        """

    return test_cls.client.execute(query, variables=variables)
        }
        """

    return test_cls.client.execute(query, variables=variables,)
