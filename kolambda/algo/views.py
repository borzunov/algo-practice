import math
import re

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from . import code_compare
from .models import Algorithm, Submit


EPS = 1e-7


def get_submit_kind(item):
    if item is None:
        return None
    if item.score < 90 - EPS:
        return 'bad'
    if item.score < 100 - EPS:
        return 'good'
    return 'perfect'


@login_required
def index(request):
    algorithms = Algorithm.objects.all()
    authors = Group.objects.get(name='algo').user_set.all()
    scoreboard = []
    for algorithm in algorithms:
        submits = []
        for author in authors:
            last_submit = Submit.objects\
                .filter(algorithm=algorithm, author=author)\
                .order_by('-date')\
                .first()
            submits.append({
                'author': author,
                'submit': last_submit,
                'submit_kind': get_submit_kind(last_submit),
            })
        scoreboard.append({
            'algorithm': algorithm,
            'submits': submits,
        })
    return render(request, 'algo/index.html', {
        'authors': authors,
        'scoreboard': scoreboard,
    })


def find_fragment_tags(algorithm_source):
    algorithm_source_lines = algorithm_source.splitlines()
    before_region_lines = None
    after_region_lines = None
    for line_index, line in enumerate(algorithm_source_lines):
        if re.search(r'^[ \t]*// *\[StartCodeRegion\]', line):
            before_region_lines = line_index
        elif (after_region_lines is None and
              re.search(r'^[ \t]*// *\[EndCodeRegion\]', line)):
            after_region_lines = len(algorithm_source_lines) - line_index - 1
    if before_region_lines is None:
        raise ValueError('[StartCodeRegion] tag not found')
    if after_region_lines is None:
        raise ValueError('[EndCodeRegion] tag not found')
    return algorithm_source_lines, before_region_lines, after_region_lines


@login_required
def check(request, algorithm_slug=None, algorithm_random=False):
    if algorithm_slug is not None:
        algorithm = get_object_or_404(Algorithm, slug=algorithm_slug)
    elif algorithm_random:
        try:
            algorithm = Algorithm.objects.order_by('?')[0]
        except IndexError:
            raise Http404('No algorithms found')
    else:
        raise ValueError('You must select algorithm or specify random mode')

    given_code = re.sub(
        r'// *\[StartCodeRegion\].*// *\[EndCodeRegion\]', r'',
        algorithm.source_code, flags=re.DOTALL
    )
    _, before_region_lines, after_region_lines = find_fragment_tags(
        algorithm.source_code)
    return render(request, 'algo/check.html', {
        'algorithm': algorithm,
        'before_region_lines': before_region_lines,
        'after_region_lines': after_region_lines,
        'given_code': given_code,
    })


def extract_code_parts(written_code, algorithm_source):
    (algorithm_source_lines, before_region_lines,
        after_region_lines) = find_fragment_tags(algorithm_source)
    expected_fragment_lines = algorithm_source_lines[before_region_lines + 1:
                                                     -(after_region_lines + 1)]
    expected_code_lines = (
        algorithm_source_lines[:before_region_lines] +
        expected_fragment_lines +
        algorithm_source_lines[-after_region_lines:]
    )
    expected_fragment = '\n'.join(expected_fragment_lines)
    expected_code = '\n'.join(expected_code_lines)

    written_code_lines = written_code.splitlines()
    written_fragment_lines = written_code_lines[before_region_lines:
                                                -after_region_lines]
    written_code = '\n'.join(written_code_lines)
    written_fragment = '\n'.join(written_fragment_lines)

    return (before_region_lines, after_region_lines,
            expected_code, written_fragment, expected_fragment)


def calculate_score(written_fragment, expected_fragment):
    written_tokens = code_compare.split_to_tokens(written_fragment)
    expected_tokens = code_compare.split_to_tokens(expected_fragment)
    distance = code_compare.levenshtein_distance(
        written_tokens, expected_tokens)
    max_distance = max(len(written_tokens), len(expected_tokens))
    score = (1.0 - distance / max_distance) * 100
    score = math.floor(score * 10) / 10
    return score, distance, max_distance


@login_required
def create_submit(request, algorithm_slug):
    try:
        written_code = request.POST['source_code'].rstrip()
        #  Set required newline character
        written_code = '\n'.join(written_code.splitlines())
        elapsed_seconds = int(request.POST['elapsed_seconds'])
    except (KeyError, ValueError):
        return redirect('algo:check', algorithm_slug=algorithm_slug)
    algorithm = get_object_or_404(Algorithm, slug=algorithm_slug)

    (before_region_lines, after_region_lines, expected_code,
        written_fragment, expected_fragment) = extract_code_parts(
        written_code, algorithm.source_code)
    score, distance, max_distance = calculate_score(
        written_fragment, expected_fragment)

    submit = Submit.objects.create(
        algorithm=algorithm,
        author=request.user,
        elapsed_seconds=elapsed_seconds,
        source_code=written_code,
        score=score)
    return render(request, 'algo/submit.html', {
        'submit': submit,
        'before_region_lines': before_region_lines,
        'after_region_lines': after_region_lines,
        'expected_code': expected_code,
        'new_submit': True,
        'score': score,
        'distance': distance,
        'max_distance': max_distance,
    })


@login_required
def history(request, author_username, algorithm_slug=None):
    author = get_object_or_404(User,
                               username=author_username, groups__name='algo')
    if algorithm_slug is not None:
        algorithm = get_object_or_404(Algorithm, slug=algorithm_slug)
        submits = Submit.objects.filter(author=author, algorithm=algorithm)
    else:
        algorithm = None
        submits = Submit.objects.filter(author=author)
    submits = submits.order_by('-pk')
    full_matches_count = sum(1 for item in submits
                             if abs(item.score - 100) < EPS)
    return render(request, 'algo/history.html', {
        'algorithm': algorithm,
        'author': author,
        'full_matches_count': full_matches_count,
        'submits': submits,
    })


@login_required
def show_submit(request, author_username, algorithm_slug, submit_id):
    author = get_object_or_404(User,
                               username=author_username, groups__name='algo')
    algorithm = get_object_or_404(Algorithm, slug=algorithm_slug)
    submit = get_object_or_404(Submit, author=author, algorithm=algorithm,
                               id=submit_id)

    (before_region_lines, after_region_lines, expected_code,
        written_fragment, expected_fragment) = extract_code_parts(
        submit.source_code, algorithm.source_code)
    score, distance, max_distance = calculate_score(
        written_fragment, expected_fragment)

    return render(request, 'algo/submit.html', {
        'submit': submit,
        'before_region_lines': before_region_lines,
        'after_region_lines': after_region_lines,
        'expected_code': expected_code,
        'new_submit': False,
        'score': score,
        'distance': distance,
        'max_distance': max_distance,
    })
