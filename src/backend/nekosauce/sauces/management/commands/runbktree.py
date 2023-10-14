import time
import threading

from django.core.management.base import BaseCommand, CommandError

from fastapi import FastAPI

from rich.progress import track

import uvicorn

import pybktree

from nekosauce.sauces.models import Sauce


class Command(BaseCommand):
    help = "Runs the BK tree server"

    def handle(self, *args, **options):
        app = FastAPI(title="NekoSauce BK Tree")

        global tree
        tree = pybktree.BKTree(lambda x, y: pybktree.hamming_distance(x[0], y[0]))

        def update_tree():
            while True:
                global tree
                tree = pybktree.BKTree(lambda x, y: pybktree.hamming_distance(x[0], y[0]), [
                    (int(sauce.hash, 2), sauce.id) for sauce in Sauce.objects.filter(status=Sauce.Status.PROCESSED).iterator()
                ])
                time.sleep(60 * 15)

        threading.Thread(target=update_tree).start()

        @app.get("/find")
        async def find(bits: str, distance: int):
            return [
                {"d": item[0], "id": item[1][1]}
                for item in sorted(tree.find((int(bits, 2), 0), distance))
            ]

        uvicorn.run(app, host="0.0.0.0", port=7171)
