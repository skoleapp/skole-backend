from rest_framework.test import APITestCase

from api.utils import READ_ONLY_MESSAGE
from core.utils import HIGH_SCHOOL, UNIVERSITY, UNIVERSITY_OF_APPLIED_SCIENCES
from tests.api.utils.school import sample_school


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
        pass

    def test_get_school_list_with_filtering(self):
        pass

    def test_get_school_detail(self):
        pass

    def test_non_safe_methods_not_allowed(self):
        # delete
        # put
        # patch
        # post
        pass


