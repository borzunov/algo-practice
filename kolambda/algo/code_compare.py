import re


def split_to_tokens(code):
    return re.split(r'(\w+|\S)', code)[1::2]


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
