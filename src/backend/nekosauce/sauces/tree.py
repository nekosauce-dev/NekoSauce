import collections

from django.core.cache import cache

import pybktree

from nekosauce.sauces.models import Sauce


global hashes_bktree
hashes_bktree = None


def distance(x, y):
    return pybktree.hamming_distance(x[0], y[0])

def load():
    global hashes_bktree
    hashes_bktree = pybktree.BKTree(
        distance,
        [
            (int(sauce.hash, 2), sauce.id)
            for sauce in Sauce.objects.filter(status=Sauce.Status.PROCESSED).iterator()
        ],
    )
