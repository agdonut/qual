from django.urls import path
from .views import recommend_trajectory

urlpatterns = [
    path('', recommend_trajectory, name='recommend'),
]