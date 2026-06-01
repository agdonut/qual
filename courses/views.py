from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import login_required

from .models import Course
from competencies.services import apply_course

from tests.models import Result, Test
from progress.models import Progress


def course_list(request):

    courses = Course.objects.all()

    return render(
        request,
        'courses/course_list.html',
        {'courses': courses}
    )

@login_required
def course_detail(request, id):

    course = get_object_or_404(
        Course,
        id=id
    )

    return render(
        request,
        'courses/course_detail.html',
        {'course': course}
    )

@login_required
def my_courses(request):
    progresses = Progress.objects.filter(user=request.user).select_related('course')

    data = []

    for p in progresses:
        total_tests = Test.objects.filter(lesson__course=p.course).count()

        passed_tests = Result.objects.filter(
            user=request.user,
            test__lesson__course=p.course
        ).values('test').distinct().count()

        data.append({
            'course': p.course,
            'score': p.score,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
        })

    return render(request, 'courses/my_courses.html', {
        'progresses': data
    })

@login_required
def complete_course(request, id):

    course = get_object_or_404(Course, id=id)

    lessons = course.lessons.all()

    tests = Test.objects.filter(lesson__in=lessons)

    results = Result.objects.filter(
        user=request.user,
        test__in=tests
    )

    if results.exists():
        avg_score = sum(r.score for r in results) / results.count()
    else:
        avg_score = 0

    Progress.objects.update_or_create(
        user=request.user,
        course=course,
        defaults={"score": avg_score}
    )
    
    apply_course(request.user, course)

    return redirect('my_courses')