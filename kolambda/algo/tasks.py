import re

from django.conf import settings
from celery import shared_task
import requests

from .models import Submit


def login_into_judge():
    session = requests.Session()
    session.post('http://acm.timus.ru/authedit.aspx', data={
        'Action': 'edit',
        'JudgeID': settings.TIMUS_JUDGE_ID,
        'Password': ''})
    return session


@shared_task
def submit_to_judge(submit_id):
    submit = Submit.objects.get(pk=submit_id)
    try:
        session = login_into_judge()

        url = 'http://acm.timus.ru/submit.aspx?space={}'.format(
            submit.algorithm.judge_space_id)
        session.post(url, data={
            'Action': 'submit',
            'JudgeID': settings.TIMUS_JUDGE_ID,
            'SpaceID': str(submit.algorithm.judge_space_id),
            'ProblemNum': str(submit.algorithm.judge_problem_id),
            'Language': str(submit.algorithm.language.judge_language_id),
            'Source': submit.source_code})
        verdict = 'Sent'
    except requests.exceptions.RequestException:
        verdict = 'Sending failed'
    submit.judge_verdict = verdict
    submit.save()

    update_judge_verdict.delay(submit_id, session, 1)


RELOAD_SCHEDULE = [
    [3, 2],          # Delay for 2 s after the first 3 queries (before 6 s)
    [3, 3],          # Delay for 3 s after the next 3 queries (before 15 s)
    [2, 10],         # Delay for 10 s after the next 2 queries (before 35 s)
    [2, 30],         # Delay for 30 s after the next 2 queries (before 95 s)
    [None, 5 * 60],  # Delay for 10 minutes after the rest of queries
]


def calculate_reload_delay(prev_attempt_no):
    for queries_count, delay in RELOAD_SCHEDULE:
        if queries_count is None or prev_attempt_no <= queries_count:
            return delay
        prev_attempt_no -= queries_count


@shared_task
def update_judge_verdict(submit_id, session, attempt_no):
    submit = Submit.objects.get(pk=submit_id)
    try:
        judge_author_id = re.match(r'\d+', settings.TIMUS_JUDGE_ID).group()
        url = ('http://acm.timus.ru/textstatus.aspx' +
               '?space={}&num={}&author={}&count=1'.format(
                   submit.algorithm.judge_space_id,
                   submit.algorithm.judge_problem_id,
                   judge_author_id))
        response = session.get(url)
        print(response.text)  # FIXME:
        fields = response.text.splitlines()[1].split('\t')
        verdict = fields[6]
        test = int(fields[7]) if fields[7] else None
    except (requests.exceptions.RequestException, IndexError, ValueError):
        verdict = 'Check failed'
        test = None
    submit.judge_verdict = verdict
    if test:
        submit.judge_test = test
    submit.save()

    if submit.get_verdict_type() == 'waiting':
        update_judge_verdict.apply_async(
            (submit_id, session, attempt_no + 1),
            countdown=calculate_reload_delay(attempt_no))
