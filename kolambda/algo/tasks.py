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
    session = login_into_judge()

    submit = Submit.objects.get(pk=submit_id)
    url = 'http://acm.timus.ru/submit.aspx?space={}'.format(
        submit.algorithm.judge_space_id)
    response = session.post(url, data={
        'Action': 'submit',
        'JudgeID': settings.TIMUS_JUDGE_ID,
        'SpaceID': str(submit.algorithm.judge_space_id),
        'ProblemNum': str(submit.algorithm.judge_problem_id),
        'Language': str(submit.algorithm.language.judge_language_id),
        'Source': submit.source_code})

    submit.judge_verdict = 'Sent'
    submit.save()

    update_judge_verdict.delay(submit_id, session, 1)


LOCAL_VERDICTS = ('Sending', 'Sent', 'Retrieving failed')
TIMUS_WAITING_VERDICTS = ('Waiting', 'Compiling', 'Running')
TIMUS_REJECTED_VERDICTS = (
    'Compilation error',
    'Wrong answer',
    'Time limit exceeded',
    'Memory limit exceeded',
    'Output limit exceeded',
    'Idleness limit exceeded',
    'Runtime error',
    'Restricted function',
)
TIMUS_ACCEPTED_VERDICTS = ('Accepted',)


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
    judge_author_id = re.match(r'\d+', settings.TIMUS_JUDGE_ID).group()
    url = ('http://acm.timus.ru/textstatus.aspx?space={}&num={}&author={}'
           .format(submit.algorithm.judge_space_id,
                   submit.algorithm.judge_problem_id,
                   judge_author_id))
    response = session.get(url)

    print(response.text)  # FIXME:
    try:
        verdict = response.text.splitlines()[1].split('\t')[6]
    except IndexError:
        verdict = 'Retrieving failed'
    submit.judge_verdict = verdict
    submit.save()

    if verdict in LOCAL_VERDICTS + TIMUS_WAITING_VERDICTS:
        update_judge_verdict.apply_async(
            (submit_id, session, attempt_no + 1),
            countdown=calculate_reload_delay(attempt_no))
