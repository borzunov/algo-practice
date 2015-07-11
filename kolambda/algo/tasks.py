import math
import re
from django.utils import timezone

import requests
from django.conf import settings
from celery import shared_task

from .models import Submit


def login_into_judge():
    session = requests.Session()
    session.post('http://acm.timus.ru/authedit.aspx', data={
        'Action': 'edit',
        'JudgeID': settings.TIMUS_JUDGE_ID,
        'Password': ''})
    return session


class JudgeAPIException(Exception):
    pass


@shared_task
def submit_to_judge(submit_id):
    submit = Submit.objects.get(pk=submit_id)
    submit.judge_verdict = 'Sending'
    submit.save()

    try:
        session = login_into_judge()

        url = 'http://acm.timus.ru/submit.aspx?space={}'.format(
            submit.algorithm.judge_space_id)
        response = session.post(url, data={
            'Action': 'submit',
            'JudgeID': settings.TIMUS_JUDGE_ID,
            'SpaceID': str(submit.algorithm.judge_space_id),
            'ProblemNum': str(submit.algorithm.judge_problem_id),
            'Language': str(submit.algorithm.language.judge_language_id),
            'Source': submit.source_code},
            allow_redirects=False)
        if response.status_code != 303:
            raise JudgeAPIException('Got status code {}, expected 303'
                                    .format(response.status_code))
        if 'status.aspx' not in response.headers['location']:
            raise JudgeAPIException('Got unexpected Location header "{}"'
                                    .format(response.headers['location']))
        verdict = 'Checking'
    except (requests.exceptions.RequestException, JudgeAPIException):
        verdict = 'Sending failed'
    submit.judge_verdict = verdict
    submit.judge_submit_date = timezone.now()
    if submit.get_verdict_type() != 'waiting':
        submit.awaiting_for_verdict = False
    submit.save()

    if submit.get_verdict_type() == 'waiting':
        update_judge_verdict.delay(submit_id, session, 1)


def invoke_submit_to_judge(submit_id):
    last_submit = Submit.objects.order_by('judge_submit_date').last()
    if last_submit is None:
        delay = 0
    else:
        last_judge_submit_date = last_submit.judge_submit_date
        if last_judge_submit_date is None:
            delay = 0
        else:
            elapsed_seconds = ((timezone.now() - last_judge_submit_date)
                               .total_seconds())
            delay = math.ceil(max(
                settings.TIMUS_SECONDS_BETWEEN_SUBMITS - elapsed_seconds, 0))
    submit_to_judge.apply_async((submit_id,), countdown=delay)


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
        if response.status_code != 200:
            raise JudgeAPIException('Got status code {}, expected 200'
                                    .format(response.status_code))
        print(response.text)  # FIXME:

        try:
            if not response.text.startswith('submit'):
                raise ValueError
            fields = response.text.splitlines()[1].split('\t')
            verdict = fields[6]
            test = int(fields[7]) if fields[7] else None
        except (ValueError, IndexError):
            raise JudgeAPIException('Invalid response text')
    except (requests.exceptions.RequestException, JudgeAPIException):
        verdict = 'Check failed'
        test = None
        # TODO: Add exception message to a judge comment field
    submit.judge_verdict = verdict
    if test:
        submit.judge_test = test
    if submit.get_verdict_type() != 'waiting':
        submit.awaiting_for_verdict = False
    submit.save()

    if submit.get_verdict_type() != 'waiting':
        # FIXME: In rare cases, if a submit will be added in the view
        # when the worker executes code right here, the same submit will be
        # processed twice (because both the view and the worker invoke
        # submit_to_judge.delay). It can lead to wrong verdicts in
        # the case when there's the significant rest of the queue (then two
        # instances of update_judge_verdict can invoke submit_to_judge.delay
        # of two different submits from the rest of the queue simultaneously
        # later).
        next_enqueued = Submit.objects.filter(awaiting_for_verdict=True)
        next_submit = next_enqueued.first()
        if next_submit is not None:
            invoke_submit_to_judge(next_submit.id)
            print('Submit with score {:.2f} have been dequeued'.format(
                  next_submit.score))  # FIXME:
        else:
            print('No submits to dequeue')  # FIXME:
    else:
        update_judge_verdict.apply_async(
            (submit_id, session, attempt_no + 1),
            countdown=calculate_reload_delay(attempt_no))
