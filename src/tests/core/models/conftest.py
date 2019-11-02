import datetime

from pytest import fixture
from django.core.files.uploadedfile import SimpleUploadedFile

from core.models import (
    Comment,
    Course,
    Resource,
    School,
    Subject,
    User,
)
from core.utils import EXAM
from core.utils import UNIVERSITY


@fixture
def user(db: fixture) -> User:
    user = User.objects.create_user(
        email="testmail@gmail.com",
        username="testuser",
        password="testpass",
    )
    return user


@fixture
def school(db: fixture) -> School:
    school = School.objects.create(
        school_type=UNIVERSITY,
        name="University of Test",
        city="Test city",
        country="Test country",
    )
    return school


@fixture
def subject(user: fixture, school: fixture) -> Subject:
    subject = Subject.objects.create(
        name="Test subject",
    )
    subject.school.add(school)
    return subject


@fixture
def course(user: fixture, school: fixture, subject: fixture) -> Course:
    course = Course.objects.create(
        name="Test course",
        code="TEST0001",
        subject=subject,
        school=school,
        creator=user,
    )
    return course


@fixture
def resource(user: fixture, course: fixture) -> Resource:
    resource = Resource.objects.create(
        resource_type=EXAM,
        title="Test exam",
        file=SimpleUploadedFile("test_exam.txt", b"file contents"),
        date=datetime.date(2019, 1, 1),
        course=course,
        creator=user,
    )
    return resource


@fixture
def comment(user: fixture, resource: fixture) -> Comment:
    comment = Comment.objects.create(
        text="This is a test comment",
        attachment=None,
        resource=resource,
        creator=user,
    )
    return comment
