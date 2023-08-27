import time
import base64

from django.core.management.base import BaseCommand, CommandError

import grequests

from nekosauce.sauces.utils import paginate
from nekosauce.sauces.tasks import calc_hashes
from nekosauce.sauces.models import Sauce
from nekosauce.sauces.sources import get_downloader


class Command(BaseCommand):
    help = "Updates all hashes for the specified fetcher/source"

    def add_arguments(self, parser):
        parser.add_argument("--limit", "-l", type=int, default=1000)
        parser.add_argument("--async-reqs", "-a", type=int, default=3)
        parser.add_argument("--chunk-size", "-c", type=int, default=128)

    def handle(self, *args, **options):
        self.stdout.write(f"Hashing sauces...")

        sauces = Sauce.objects.filter(downloaded=False)[: options["limit"]]
        reqs = []

        for sauce in sauces:
            downloaders = [(get_downloader(url), url) for url in sauce.file_urls]
            downloaders = [d for d in downloaders if d[0] is not None]

            downloader, url = downloaders[0] if downloaders else (None, None)

            if downloader is None:
                return False, "No downloader found for URLs {}".format(
                    ", ".join(sauce.file_urls)
                )

            reqs.append(downloader().download_request(url))

        req_chunks = paginate(reqs, options["chunk_size"])

        current_index = 0

        while True:
            for index, response in grequests.imap_enumerated(req_chunks[0], size=options["async_reqs"]):
                if response is None:
                    # Failed downloading the image
                    continue

                if current_index > options["limit"]:
                    return

                sauce = sauces[index]

                calc_hashes.send(sauce.id, base64.b64encode(response.content).decode(), False)

                self.stdout.write(
                    self.style.SUCCESS(f"ADDING")
                    + f": {sauce.source_site_id} - {sauce.title}"
                )
            
            del req_chunks[0]

            if len(req_chunks) == 0:
                break

        self.stdout.write(self.style.SUCCESS("Done!"))
