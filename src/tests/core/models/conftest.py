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
def user(db):
    user = User.objects.create(
        email="testmail@gmail.com",
        username="testuser",
        password="testpass",
    )
    return user


@pytest.fixture
def school(db):
    school = School.objects.create(
        school_type=UNIVERSITY,
        name="University of Test",
        city="Test city",
        country="Test country",
    )
    return school


@pytest.fixture
def faculty(school):
    faculty = Faculty.objects.create(
        name="Test faculty",
        university=school,
    )
    return faculty


@pytest.fixture
def facility(faculty):
    facility = Facility.objects.create(
        name="Test facility",
        faculty=faculty,
    )
    return facility


@pytest.fixture
def subject(user, faculty, school):
    subject = Subject.objects.create(
        name="Test subject",
    )
    subject.faculty.add(faculty)
    subject.school.add(school)
    return subject


@pytest.fixture
def course(user, school, subject):
    course = Course.objects.create(
        name="Test course",
        code="TEST0001",
        subject=subject,
        school=school,
        creator=user,
    )
    return course


@pytest.fixture
def resource(user, course):
    resource = Resource.objects.create(
        resource_type=EXAM,
        title="Test exam",
        file=SimpleUploadedFile("test_exam.txt", b"file contents"),
        date=datetime.date(2019, 1, 1),
        course=course,
        creator=user,
    )
    return resource


@pytest.fixture
def comment(user, resource):
    comment = Comment.objects.create(
        text="This is a test comment",
        attachment=None,
        resource=resource,
        creator=user,
    )
    return comment
