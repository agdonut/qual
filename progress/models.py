from django.db import models
from django.conf import settings
from courses.models import Course

class Progress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    score = models.FloatField(default=0)     # r_i

    def __str__(self):
        return f"{self.user} - {self.course}"