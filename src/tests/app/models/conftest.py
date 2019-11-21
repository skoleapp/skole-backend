import datetime

from django.core.files.uploadedfile import SimpleUploadedFile
from pytest import fixture

from app.models.course import Course
from app.models.resource import Resource
from app.models.school import School
from app.models.subject import Subject
from app.models.user import User


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
    subject.schools.add(school)
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
        date=datetime.date(2019, 1, 1),
        course=course,
        creator=user,
    )
    resource.file = SimpleUploadedFile("test_exam.txt", b"file contents"),
    return resource


@fixture
def comment(user: fixture, resource: fixture) -> ResourceComment:
    comment = ResourceComment.objects.create(
        text="This is a test comment",
        attachment=None,
        resource=resource,
        creator=user,
    )
    return comment
