from django.db import models
from django.conf import settings


class Competency(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class UserCompetency(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="competencies"
    )
    competency = models.ForeignKey(
        Competency,
        on_delete=models.CASCADE,
        related_name="user_levels"
    )

    level = models.FloatField(default=0)

    class Meta:
        unique_together = ("user", "competency")