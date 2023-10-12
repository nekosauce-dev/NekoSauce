import collections

from django.core.cache import cache

import pybktree

from nekosauce.sauces.models import Sauce


def distance(x, y):
    return pybktree.hamming_distance(x[0], y[0])

def load():
    return pybktree.BKTree(
        distance,
        [
            (int(sauce.hash, 2), sauce.id)
            for sauce in Sauce.objects.filter(status=Sauce.Status.PROCESSED).iterator()
        ],
    )
