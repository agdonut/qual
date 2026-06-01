from .models import UserCompetency
from courses.models import CourseCompetency


def apply_course(user, course):
    course_competencies = CourseCompetency.objects.filter(course=course)

    for cc in course_competencies:
        uc, _ = UserCompetency.objects.get_or_create(
            user=user,
            competency=cc.competency,
            defaults={"level": 0}
        )

        delta = cc.gain * (1 - uc.level / 100)

        uc.level = min(100, uc.level + delta)
        uc.save()