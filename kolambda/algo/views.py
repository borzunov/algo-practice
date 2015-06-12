from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from .code_processing import EditableSourceRegion, CodeComparer
from .models import Algorithm, Submit


EPS = 1e-7


def get_submit_kind(item):
    if item is None:
        return None
    if item.score < 80 - EPS:
        return 'bad'
    if item.score < 95 - EPS:
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
            last_submit = (Submit.objects
                                 .filter(algorithm=algorithm, author=author)
                                 .order_by('-date')
                                 .first())
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

    region = EditableSourceRegion(algorithm.source_code)
    given_code_lines = (
        region.lines[:region.lines_before] +
        [''] +
        region.lines[-region.lines_after:])
    given_code = '\n'.join(given_code_lines)

    return render(request, 'algo/check.html', {
        'algorithm': algorithm,
        'given_code': given_code,
        'editable_region': region,
    })


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

    comparer = CodeComparer(written_code, algorithm.source_code)
    submit = Submit.objects.create(
        algorithm=algorithm,
        author=request.user,
        elapsed_seconds=elapsed_seconds,
        source_code=written_code,
        score=comparer.score)

    return redirect('algo:show_new_submit',
                    author_username=request.user.username,
                    algorithm_slug=algorithm.slug, submit_id=submit.id)


@login_required
def history(request, author_username, algorithm_slug=None):
    author = get_object_or_404(User, username=author_username)
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
def show_submit(request, author_username, algorithm_slug, submit_id,
                new_submit=False):
    author = get_object_or_404(User, username=author_username)
    algorithm = get_object_or_404(Algorithm, slug=algorithm_slug)
    submit = get_object_or_404(Submit, author=author, algorithm=algorithm,
                               id=submit_id)

    comparer = CodeComparer(submit.source_code, algorithm.source_code)

    return render(request, 'algo/submit.html', {
        'comparer': comparer,
        'editable_region': comparer.editable_region,
        'new_submit': new_submit,
        'submit': submit,
    })
