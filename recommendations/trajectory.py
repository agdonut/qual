import math
import copy
from progress.models import Progress
from courses.models import Course

TRAJECTORY_LENGTH = 5
BEAM_WIDTH = 5
MIN_COMPETENCY_LEVEL = 0.01

K_MAX = 1
MAX_TIME = 80
alpha, beta, gamma = 0.3, 0.5, 0.2
LAMBDA = 0.1


def calculate_s_current(user):
    progress = Progress.objects.filter(user=user)

    sum_p = 0
    n = 0
    w = 0

    for p in progress:
        sum_p += p.score * p.course.weight
        n += 1
        w += p.course.weight

    if n == 0:
        return 0, 0

    return sum_p / w, n


def get_finished_courses(user):
    progress = Progress.objects.filter(user=user)

    courses = []

    for p in progress:
        courses.append(p.course)

    return courses


def copy_user_state(user):
    return {
        "competencies": {
            uc.competency_id: uc.level
            for uc in user.competencies.all()
        }
    }


def apply_course_effect(state, course):
    for cc in course.coursecompetency_set.select_related(
        "competency"
    ):

        current = state["competencies"].get(
            cc.competency_id,
            0
        )

        delta = cc.gain * (1 - current)

        state["competencies"][cc.competency_id] = min(
            1,
            current + delta
        )


def get_available_competencies(state):
    return {
        competency_id
        for competency_id, level
        in state["competencies"].items()
        if level >= MIN_COMPETENCY_LEVEL
    }


def get_course_competency_context(course, user):
    course_comps = course.coursecompetency_set.select_related(
        "competency"
    )

    result = []

    for cc in course_comps:

        uc = user.competencies.filter(
            competency=cc.competency
        ).first()

        result.append({
            "name": cc.competency.name,
            "user_level": uc.level if uc else 0,
            "gain": cc.gain,
        })

    return result


def generate_trajectories(user):
    s0, n0 = calculate_s_current(user)
    
    completed_courses = get_finished_courses(user)

    completed_course_ids = {
        c.id for c in completed_courses
    }

    all_courses = list(
        Course.objects.all()
    )

    initial_state = copy_user_state(user)

    initial_competencies = get_available_competencies(
        initial_state
    )

    # стартовые ветки
    beams = []

    for course in all_courses:

        if course.id in completed_course_ids:
            continue

        course_competency_ids = set(
            course.coursecompetency_set.values_list(
                "competency_id",
                flat=True
            )
        )

        course_competencies = course.coursecompetency_set.select_related("competency")

        # считаем средний/макс уровень пользователя по компетенциям курса
        total = 0
        count = 0

        for cc in course_competencies:
            user_level = initial_state["competencies"].get(cc.competency_id, 0)
            total += user_level
            count += 1

        if count == 0:
            continue  # если у курса нет компетенций, то пропуск

        avg_user_level = total / count

        
        # не слишком большая сложность
        if avg_user_level * 1.5 + 0.05 < course.difficulty:
            continue

        # курс должен пересекаться с компетенциями пользователя
        if not initial_competencies.intersection(
            course_competency_ids
        ):
            continue

        simulated_state = copy.deepcopy(initial_state)

        apply_course_effect(
            simulated_state,
            course
        )

        path = [course]

        score_data = calculate_trajectory_score(
            path,
            copy.deepcopy(initial_state),
            completed_course_ids,
            s0
        )

        beams.append({
            "path": path,
            "used_ids": {course.id},
            "score": score_data["score"],
            "success": score_data["success"],
            "delta_k": score_data["delta_k"],
            "time": score_data["time"],
            "T": score_data["T"],
        })

    # стартовые курсы
    beams.sort(
        key=lambda x: (
            x["score"],
            x["success"],
            x["delta_k"]
        ),
        reverse=True
    )

    beams = beams[:BEAM_WIDTH]

    # beam search
    for _ in range(TRAJECTORY_LENGTH - 1):

        new_beams = []

        for beam in beams:

            expanded = False

            for next_course in all_courses:

                if next_course.id in beam["used_ids"]:
                    continue

                if next_course.id in completed_course_ids:
                    continue

                last_course = beam["path"][-1]

                if next_course.difficulty > last_course.difficulty + 0.3:
                    continue
                
                new_path = beam["path"] + [next_course]

                next_course_competency_ids = set(
                    next_course.coursecompetency_set.values_list(
                        "competency_id",
                        flat=True
                    )
                )

                if not initial_competencies.intersection(
                    next_course_competency_ids
                ):
                    continue

                score_data = calculate_trajectory_score(
                    new_path,
                    copy.deepcopy(initial_state),
                    completed_course_ids,
                    s0
                )

                new_beams.append({
                    "path": new_path,
                    "used_ids": (
                        beam["used_ids"] |
                        {next_course.id}
                    ),
                    "score": score_data["score"],
                    "success": score_data["success"],
                    "delta_k": score_data["delta_k"],
                    "time": score_data["time"],
                    "T": score_data["T"],
                })

                expanded = True

            if not expanded:
                new_beams.append(beam)

        new_beams.sort(
            key=lambda x: (
                x["score"],
                x["success"],
                x["delta_k"]
            ),
            reverse=True
        )

        # оставляем k лучших
        beams = new_beams[:BEAM_WIDTH]

    # финальные траектории
    trajectories = []

    for beam in beams:

        trajectories.append({
            "courses": beam["path"],
            "score": beam["score"],
            "delta_k": beam["delta_k"],
            "success": beam["success"] * 100,
            "time": beam["time"],
            "T": beam["T"],
            "competencies": (
                get_course_competency_context(
                    beam["path"][0],
                    user
                )
            ),
        })

    trajectories.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return trajectories


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def p_i(K_u, S_current_value, D_i):
    return 1 / (1 + math.exp(-(K_u + 0.9*S_current_value - D_i)))
    #return (K_u * S_current_value / (K_u + D_i))


def delta_k(courses, state):
    total = 0

    for course in courses:
        for cc in course.coursecompetency_set.all():

            K_u = state["competencies"].get(cc.competency_id, 0)

            g_i = cc.gain

            rep_i = state["repeat_count"].get(cc.competency_id, 0)

            total += g_i * (1 - K_u / K_MAX) * math.exp(-LAMBDA * rep_i)

    return total


def s_hat(trajectory_p):
    if not trajectory_p:
        return 0
    print(trajectory_p)
    return sum(trajectory_p) / len(trajectory_p)


def time_T(courses):
    total = sum(c.duration for c in courses)
    return total / (MAX_TIME * len(courses)), total


def F(delta_k_value, s_hat_value, time_value):
    return alpha * delta_k_value + beta * s_hat_value - gamma * time_value


def calculate_trajectory_score(
    courses,
    state,
    completed_course_ids,
    s0
):

    competencies = state["competencies"]
    repeat_count = state.setdefault("repeat_count", {})
    S_current = s0 #state.get("S_current", 0.5)
 
    before = copy.deepcopy(competencies)

    def compute_K_u():
        if not competencies:
            return 0
        return sum(competencies.values()) / len(competencies)

    p_list = []

    for course in courses:

        K_u = compute_K_u()

        p = p_i(
            K_u,
            S_current,
            course.difficulty
        )

        if course.id in completed_course_ids:
            p *= 0.5

        p = max(0.001, min(1, p))

        p_list.append(p)

        for cc in course.coursecompetency_set.all():
            comp_id = cc.competency_id
            repeat_count[comp_id] = (
                repeat_count.get(comp_id, 0) + 1
            )

        apply_course_effect(state, course)
        
        S_current = (
            S_current * 0.7 +
            p * 0.3
        )

    state["S_current"] = S_current
    #print(state["S_current"])

    after = competencies

    DK = 0

    all_ids = set(before.keys()) | set(after.keys())

    for comp_id in all_ids:

        b = before.get(comp_id, 0)
        a = after.get(comp_id, 0)

        gain = max(0, a - b)

        rep_penalty = math.exp(
            -LAMBDA * repeat_count.get(comp_id, 0)
        )

        DK += gain * rep_penalty

    S_hat_value = s_hat(p_list)

    T, t_hours = time_T(courses)

    score = F(
        DK,
        S_hat_value,
        T
    )

    return {
        "score": score,
        "delta_k": DK,
        "success": S_hat_value,
        "time": t_hours,
        "T": T
    }