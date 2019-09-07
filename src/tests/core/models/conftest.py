import datetime

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from core.models import (
    User, School, Comment, Course,
    Subject, Faculty, Facility, Resource
)
from core.utils import EXAM
from core.utils import UNIVERSITY


@pytest.fixture
def user():
    def wrapper(**params):
        fields = {
            "email": "testmail@gmail.com",
            "username": "testuser",
            "password": "testpass",
        }
        fields.update(**params)
        return User.objects.create(**fields)

    return wrapper


@pytest.fixture
def school():
    def wrapper(**params):
        fields = {
            "school_type": UNIVERSITY,
            "name": "University of Test",
            "city": "Test city",
            "country": "Test country",
        }
        fields.update(**params)
        return School.objects.create(**fields)

    return wrapper


@pytest.fixture
def faculty(school):
    def wrapper(**params):
        fields = {
            "name": "Test faculty",
            "university": school(),
        }
        fields.update(**params)
        return Faculty.objects.create(**fields)

    return wrapper


@pytest.fixture
def facility(faculty):
    def wrapper(**params):
        fields = {
            "name": "Test facility",
            "faculty": faculty(),
        }
        fields.update(**params)
        return Facility.objects.create(**fields)

    return wrapper


@pytest.fixture
def subject(user, faculty, school):
    def wrapper(**params):
        fields = {
            "name": "Test subject",
        }
        fields.update(**params)
        subject = Subject.objects.create(**fields)
        subject.faculty.add(faculty())
        subject.school.add(school())
        return subject

    return wrapper


@pytest.fixture
def course(user, school, subject):
    def wrapper(**params):
        fields = {
            "name": "Test course",
            "code": "TEST0001",
            "subject": subject(),
            "school": school(),
            "creator": user(),
        }
        fields.update(**params)
        return Course.objects.create(**fields)

    return wrapper


@pytest.fixture
def resource(user, course):
    def wrapper(**params):
        fields = {
            "resource_type": EXAM,
            "title": "Test exam",
            "file": SimpleUploadedFile("test_exam.txt", "file contents"),
            "date": datetime.date(2019, 1, 1),
            "course": course(),
            "creator": user(),
        }
        fields.update(**params)
        return Resource.objects.create(**fields)

    return wrapper


@pytest.fixture
def comment(user, resource):
    def wrapper(**params):
        fields = {
            "text": "This is a test comment",
            "attachment": None,
            "resource": resource(),
            "creator": user(),
        }
        fields.update(**params)
        return Comment.objects.create(**fields)

    return wrapper
