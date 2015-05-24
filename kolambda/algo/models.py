from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify


class Algorithm(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=60, blank=True)
    source_code = models.TextField()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        # TODO: Unique and safe (non-empty) slugs
        super(Algorithm, self).save(*args, **kwargs)


class Submit(models.Model):
    algorithm = models.ForeignKey(Algorithm)
    author = models.ForeignKey(User)
    date = models.DateTimeField(auto_now_add=True)
    elapsed_seconds = models.IntegerField()
    source_code = models.TextField()
    score = models.FloatField()

    def __str__(self):
        return '{}: {} (score {:.1f})'.format(
            self.author, self.algorithm, self.score)
