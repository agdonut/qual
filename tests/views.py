from django.shortcuts import render, get_object_or_404
from .models import Test, Answer, Result
from progress.models import Progress


def test_detail(request, id):
    test = get_object_or_404(Test, id=id)

    if request.method == 'POST':

        questions = test.question_set.all()

        correct_answers = 0

        for question in questions:

            selected_answer_id = request.POST.get(
                f'question_{question.id}'
            )

            if selected_answer_id:

                answer = Answer.objects.get(id=selected_answer_id)

                if answer.is_correct:
                    correct_answers += 1

        total_questions = questions.count()

        score = correct_answers / total_questions

        Result.objects.create(
            user=request.user,
            test=test,
            score=score
        )
        
        Progress.objects.create(
            user=request.user,
            course=test.lesson.course,
            score=0
        )
        

        return render(request, 'tests/result.html', {
            'test': test,
            'score': score,
            'correct_answers': correct_answers,
            'total_questions': total_questions
        })

    return render(request, 'tests/test_detail.html', {
        'test': test
    })