from django.conf import settings
from celery import shared_task
import requests

from .models import Submit


@shared_task
def submit_to_judge(submit_id):
    submit = Submit.objects.get(pk=submit_id)
    url = 'http://acm.timus.ru/submit.aspx?space={}'.format(
        submit.algorithm.judge_space_id)
    response = requests.post(url, data={
        'Action': 'submit',
        'JudgeID': settings.TIMUS_JUDGE_ID,
        'SpaceID': str(submit.algorithm.judge_space_id),
        'ProblemNum': str(submit.algorithm.judge_problem_id),
        'Language': str(submit.algorithm.language.judge_language_id),
        'Source': submit.source_code})
    submit.judge_verdict = 'Sent'
    submit.save()
    print(response.cookies)  # FIXME:
