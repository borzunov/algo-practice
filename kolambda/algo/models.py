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


class Submit(models.Model):
    algorithm = models.ForeignKey(Algorithm)
    author = models.ForeignKey(User)
    date = models.DateTimeField(auto_now_add=True)
    elapsed_seconds = models.IntegerField()
    source_code = models.TextField()
    score = models.FloatField()

    judge_verdict = models.CharField(blank=True, max_length=255)

    def __str__(self):
        return '{}: {} (score {:.1f})'.format(
            self.author, self.algorithm, self.score)
