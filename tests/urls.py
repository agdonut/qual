from django.urls import path
from . import views

urlpatterns = [
    path('<int:id>/', views.test_detail, name='test_detail'),
]