from django.db import models

from .course import Course
from .user import User


class Resource(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to="uploads/resources")
    date = models.DateField(null=True, blank=True)  # The poster can specify when the resource is dated.
    points = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL)  # TODO: custom deletor, which marks the user as some anonymous user
    created_at = models.DateField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.title} by {self.creator.name}"

    class Meta:
        abstract = True


class ExamResource(Resource):
    pass


class NoteResource(Resource):
    pass


class ExerciseResource(Resource):
    pass


class OtherResource(Resource):
    pass
