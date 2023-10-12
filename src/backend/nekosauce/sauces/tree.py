from multiprocessing import Manager

import collections

import pybktree

from nekosauce.sauces.models import Sauce


manager = Manager()
namespace = manager.Namespace()


def load_tree():
    if not hasattr(namespace, "tree"):
        Hash = collections.namedtuple("Hash", "bits id")
        namespace.tree = pybktree.BKTree(
            lambda x, y: pybktree.hamming_distance(x.bits, y.bits),
            [
                Hash(int(sauce.hash, 2), sauce.id)
                for sauce in Sauce.objects.filter(status=Sauce.Status.PROCESSED)
            ],
        )


get_tree = lambda: namespace.tree
