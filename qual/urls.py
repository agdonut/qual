from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # список курсов
    path('', include('courses.urls')),
    path('courses/', include('courses.urls')),

    path("users/", include("users.urls")),

    # приложения
    path('tests/', include('tests.urls')),
    path('recommend/', include('recommendations.urls')),
    # LOGIN
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    #path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
]