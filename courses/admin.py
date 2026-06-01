from django.contrib import admin
from .models import Course, CourseCompetency, Lesson

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

class CourseCompetencyInline(admin.TabularInline):
    model = CourseCompetency
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = [CourseCompetencyInline, LessonInline]