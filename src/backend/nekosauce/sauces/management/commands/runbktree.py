from django.core.management.base import BaseCommand, CommandError

from fastapi import FastAPI

import uvicorn

from nekosauce.sauces import tree


class Command(BaseCommand):
    help = "Runs the BK tree server"

    def handle(self, *args, **options):
        app = FastAPI(title="NekoSauce BK Tree")

        bktree = tree.load()

        @app.get("/find")
        async def find(bits: str, distance: int):
            return [
                {"d": item[0], "h": item[1][0], "id": item[1][1]}
                for item in sorted(bktree.find((int(bits, 2), 0), distance))
            ]

        uvicorn.run(app, host="0.0.0.0", port=7171)
