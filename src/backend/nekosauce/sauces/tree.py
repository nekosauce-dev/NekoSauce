import collections

from django.core.cache import cache

import pybktree

from nekosauce.sauces.models import Sauce


def load():
    Hash = collections.namedtuple("Hash", "bits id")
    return pybktree.BKTree(
        lambda x, y: pybktree.hamming_distance(x.bits, y.bits),
        [
            Hash(int(sauce.hash, 2), sauce.id)
            for sauce in Sauce.objects.filter(status=Sauce.Status.PROCESSED).iterator()
        ],
    )
