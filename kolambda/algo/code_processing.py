import math
import re


class EditableSourceRegion:
    def __init__(self, algorithm_source):
        self.lines = algorithm_source.splitlines()
        lines_before = None
        lines_after = None
        for line_index, line in enumerate(self.lines):
            if re.search(r'^[ \t]*// *\[StartCodeRegion\]', line):
                lines_before = line_index
            elif (lines_after is None and
                  re.search(r'^[ \t]*// *\[EndCodeRegion\]', line)):
                lines_after = (len(self.lines) - line_index - 1)
        if lines_before is None:
            raise ValueError('[StartCodeRegion] tag not found')
        if lines_after is None:
            raise ValueError('[EndCodeRegion] tag not found')
        self.lines_before = lines_before
        self.lines_after = lines_after


def split_to_tokens(code):
    return re.findall(r'\w+|\S', code)


def levenshtein_distance(a, b):
    M = len(a)
    N = len(b)
    dp = [[0 for j in range(N + 1)] for i in range(M + 1)]
    for i in range(M + 1):
        for j in range(N + 1):
            if i == 0 or j == 0:
                dp[i][j] = i + j
                continue
            dp[i][j] = min(
                dp[i][j - 1] + 1,
                dp[i - 1][j] + 1,
                dp[i - 1][j - 1] + (a[i - 1] != b[j - 1]),
            )
    return dp[M][N]


class CodeComparer:
    def _calculate_score(self):
        written_tokens = split_to_tokens(self.written_fragment)
        expected_tokens = split_to_tokens(self.expected_fragment)
        self.distance = levenshtein_distance(written_tokens, expected_tokens)
        self.max_distance = max(len(written_tokens), len(expected_tokens))
        score = (1.0 - self.distance / self.max_distance) * 100
        self.score = math.floor(score * 10) / 10

    def __init__(self, submit_source, algorithm_source):
        region = EditableSourceRegion(algorithm_source)
        self.editable_region = region
        expected_fragment_lines = region.lines[region.lines_before + 1:
                                               -(region.lines_after + 1)]
        self.expected_fragment = '\n'.join(expected_fragment_lines)

        written_code_lines = submit_source.splitlines()
        written_fragment_lines = written_code_lines[region.lines_before:
                                                    -region.lines_after]
        self.written_fragment = '\n'.join(written_fragment_lines)

        expected_code_lines = (
            region.lines[:region.lines_before] +
            expected_fragment_lines +
            region.lines[-region.lines_after:])
        self.expected_code = '\n'.join(expected_code_lines)

        self.written_code = submit_source

        self._calculate_score()
