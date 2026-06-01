from django.contrib import admin
from .models import Competency, UserCompetency


admin.site.register(Competency)
admin.site.register(UserCompetency)