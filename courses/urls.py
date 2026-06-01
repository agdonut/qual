from django.urls import path
from .views import (
    course_list,
    course_detail,
    complete_course,
    my_courses
)

urlpatterns = [
    path('', course_list, name='course_list'),
    
    path('<int:id>/', course_detail, name='course_detail'),
    path('my/', my_courses, name='my_courses'),
    path('<int:id>/complete/', complete_course, name='complete_course'),
]