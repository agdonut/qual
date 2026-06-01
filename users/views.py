from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from progress.models import Progress


@login_required
def profile_view(request):

    user = request.user

    progresses = Progress.objects.filter(
        user=user
    ).select_related("course")

    completed_courses = progresses

    context = {
        "user_obj": user,
        "progresses": progresses,
        "completed_courses": completed_courses,
        "competencies": user.competencies.select_related("competency")
    }

    return render(
        request,
        "users/profile.html",
        context
    )