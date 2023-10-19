import time
import threading

from django.core.management.base import BaseCommand, CommandError

from fastapi import FastAPI

from rich.progress import track

import uvicorn

import vptree

from nekosauce.sauces.models import Sauce


class Command(BaseCommand):
    help = "Runs the VP tree server"

    def handle(self, *args, **options):
        app = FastAPI(title="NekoSauce VP Tree")

        global tree
        tree = vptree.VPTree()

        def update_tree():
            while True:
                global tree
                tree = vptree.VPTree([
                    (int(sauce.hash, 2), sauce.id) for sauce in Sauce.objects.filter(status=Sauce.Status.PROCESSED).iterator()
                ], lambda x, y: bin(x[0] ^ y[0]).count("1"))
                time.sleep(60 * 15)

        threading.Thread(target=update_tree).start()

        @app.get("/find")
        async def find(bits: str, distance: int, limit: int = 50):
            return [
                {"d": item[1], "id": item[0][1]}
                for item in sorted(tree.within((int(bits, 2), 0), distance))
            ][:limit]

        uvicorn.run(app, host="0.0.0.0", port=7171)
