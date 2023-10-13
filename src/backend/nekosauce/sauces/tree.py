import pybktree

from nekosauce.sauces.models import Sauce


def load():
    return pybktree.BKTree(
        lambda x, y: pybktree.hamming_distance(x[0], y[0]),
        [
            (int(sauce.hash, 2), sauce.id)
            for sauce in Sauce.objects.filter(status=Sauce.Status.PROCESSED).iterator()
        ],
    )
