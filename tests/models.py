from django.db import models
from courses.models import Lesson

class Test(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)

class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    text = models.TextField()

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

class Result(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    score = models.FloatField(default=0)