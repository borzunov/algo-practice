from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify


class Language(models.Model):
    name = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=60)

    judge_language_id = models.IntegerField()

    def __str__(self):
        return self.name


class Algorithm(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=60)
    language = models.ForeignKey(Language)
    source_code = models.TextField()

    judge_space_id = models.IntegerField(blank=True, null=True)
    judge_problem_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

    def is_checkable_via_judge(self):
        return (self.judge_space_id is not None and
                self.judge_problem_id is not None)


#  Because of particularity of verdicts handling, a verdict mustn't be
#  a prefix of another verdict
JUDGE_VERDICTS = {
    'Enqueued':                ('UK', 'waiting'),
    'Sending':                 ('UK', 'waiting'),
    'Failed to send':          ('ERR', 'error'),
    'Checking':                ('UK', 'waiting'),
    'Failed to check':         ('ERR', 'error'),

    'Waiting':                 ('UK', 'waiting'),
    'Compiling':               ('UK', 'waiting'),
    'Running':                 ('UK', 'waiting'),

    'Compilation error':       ('CE', 'rejected'),
    'Wrong answer':            ('WA', 'rejected'),
    'Time limit exceeded':     ('TL', 'rejected'),
    'Memory limit exceeded':   ('ML', 'rejected'),
    'Output limit exceeded':   ('OL', 'rejected'),
    'Idleness limit exceeded': ('IL', 'rejected'),
    'Runtime error':           ('RE', 'rejected'),
    'Restricted function':     ('RF', 'rejected'),

    'Accepted':                ('AC', 'accepted'),
}


def get_judge_verdict_params(verdict):
    for key, value in JUDGE_VERDICTS.items():
        if verdict.startswith(key):
            return value
    return ('?', 'unknown')


class Submit(models.Model):
    algorithm = models.ForeignKey(Algorithm)
    author = models.ForeignKey(User)
    date = models.DateTimeField(auto_now_add=True)
    elapsed_seconds = models.IntegerField()
    source_code = models.TextField()
    score = models.FloatField()

    judge_submit_date = models.DateTimeField(blank=True, null=True)
    judge_verdict = models.CharField(blank=True, max_length=255)
    judge_test = models.IntegerField(blank=True, null=True)
    judge_comment = models.TextField(blank=True)
    awaiting_for_verdict = models.BooleanField()

    def __str__(self):
        return '{}: {} (score {:.1f})'.format(
            self.author, self.algorithm, self.score)

    def get_short_verdict(self):
        res = get_judge_verdict_params(self.judge_verdict)[0]
        if self.judge_test is not None:
            res += ' {}'.format(self.judge_test)
        return res

    def get_full_verdict(self):
        res = self.judge_verdict
        if self.judge_test is not None:
            res += ' on test {}'.format(self.judge_test)
        return res

    def get_verdict_type(self):
        return get_judge_verdict_params(self.judge_verdict)[1]

    def get_verdict_kind(self):
        verdict_type = self.get_verdict_type()
        if verdict_type == 'rejected':
            return 'bad'
        if verdict_type == 'accepted':
            return 'good'
        return 'unknown'

    def is_scores_visible(self):
        return not self.judge_verdict or self.get_verdict_kind() == 'good'

    EPS = 1e-7

    GOOD_SCORE = 70
    PERFECT_SCORE = 90

    def get_kind(self):
        if self.judge_verdict:
            verdict_kind = self.get_verdict_kind()
            if verdict_kind in ('bad', 'unknown'):
                return verdict_kind
        if self.score > Submit.PERFECT_SCORE - Submit.EPS:
            return 'perfect'
        if self.score > Submit.GOOD_SCORE - Submit.EPS:
            return 'good'
        return 'bad'
