from django.shortcuts import render
from courses.models import Course
from progress.models import Progress
from .trajectory import generate_trajectories
from django.contrib.auth.decorators import login_required




@login_required
def recommend_trajectory(request):
    user = request.user

    trajectories = generate_trajectories(user)

    return render(request, 'recommendations/list.html', {
        'trajectories': trajectories
    })