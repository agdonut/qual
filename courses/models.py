from django.db import models
from django.urls import reverse

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image_url = models.URLField(blank=True, null=True)

    difficulty = models.FloatField(default=1)
    duration = models.FloatField(default=1)
    
    competencies = models.ManyToManyField(
        "competencies.Competency",
        through="CourseCompetency",
        related_name="courses"
    )
    weight = models.FloatField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("course_detail", args=[self.id])

class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons"
    )

    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.title

class CourseCompetency(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    competency = models.ForeignKey("competencies.Competency", on_delete=models.CASCADE)
    gain = models.FloatField(default=0)

    class Meta:
        unique_together = ("course", "competency")