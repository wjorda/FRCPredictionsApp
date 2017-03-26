# Taken From http://stackoverflow.com/questions/32551610/overlapping-probability-of-two-normal-distribution-with-scipy

from numpy import roots, log
from scipy.stats import norm


def solve_norm_intersect(m1, m2, std1, std2):
    a = 1 / (2 * std1 ** 2) - 1 / (2 * std2 ** 2)
    b = m2 / (std2 ** 2) - m1 / (std1 ** 2)
    c = m1 ** 2 / (2 * std1 ** 2) - m2 ** 2 / (2 * std2 ** 2) - log(std2 / std1)
    return roots([a, b, c])


def get_overlap(m1, m2, std1, std2):
    # Get point of intersect
    result = solve_norm_intersect(m1, m2, std1, std2)

    r = result[0]

    # integrate
    return norm.cdf(r, m2, std2)
