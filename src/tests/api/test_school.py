from rest_framework import status
from rest_framework.test import APITestCase

from api.utils import READ_ONLY_MESSAGE
from core.utils import HIGH_SCHOOL, UNIVERSITY, UNIVERSITY_OF_APPLIED_SCIENCES
from tests.api.utils.school import (
    SCHOOL_LIST_API_URL,
    sample_school,
    school_detail_api_url,
    school_list_filter_api_url,
)


class SchoolAPITests(APITestCase):
    def setUp(self):
        self.uni1 = sample_school(school_type=UNIVERSITY)
        self.uni2 = sample_school(school_type=UNIVERSITY)
        self.high_school = sample_school(school_type=HIGH_SCHOOL)
        self.uas = sample_school(school_type=UNIVERSITY_OF_APPLIED_SCIENCES)

    def tearDown(self):
        self.uni1.delete()
        self.uni2.delete()
        self.high_school.delete()
        self.uas.delete()

    def test_get_school_list(self):
        res = self.client.get(SCHOOL_LIST_API_URL)
        assert res.status_code == status.HTTP_200_OK
        assert len(res.data["results"]) == 4

        results = res.data["results"]

        # results should come in alphabetical order based on the name
        assert results == sorted(results, key=lambda r: r["name"])

        assert results[0]["name"] == "Test high school"
        assert results[1]["city"] == "Turku"
        assert results[2]["school_type"] == "University"
        assert results[3]["country"] == "Finland"

    def test_get_school_list_with_filtering(self):
        # FIXME: school_list_filter_api_url() is not working
        res = self.client.get(school_list_filter_api_url(UNIVERSITY_OF_APPLIED_SCIENCES))
        assert res.status_code == status.HTTP_200_OK

    def test_get_school_detail(self):
        res = self.client.get(school_detail_api_url(self.uni1.id))
        assert res.status_code == status.HTTP_200_OK
        assert len(res.data) == 5  # should return 5 fields
        assert res.data["name"] == "Test university"
        assert res.data["school_type"] == "University"
        assert res.data["city"] == "Turku"
        assert res.data["country"] == "Finland"

    def test_non_safe_methods_not_allowed(self):
        url = school_detail_api_url(self.uni1)
        assert self.client.delete(url, {}).status_code == status.HTTP_403_FORBIDDEN
        assert self.client.put(url, {}).status_code == status.HTTP_403_FORBIDDEN
        assert self.client.patch(url, {}).status_code == status.HTTP_403_FORBIDDEN
        assert self.client.post(url, {}).status_code == status.HTTP_403_FORBIDDEN
