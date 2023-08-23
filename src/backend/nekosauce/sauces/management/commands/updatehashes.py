import time

from django.core.management.base import BaseCommand, CommandError

import grequests

from nekosauce.sauces.models import Sauce
from nekosauce.sauces.sources import get_downloader
from nekosauce.sauces.tasks import calc_hashes


class Command(BaseCommand):
    help = "Updates all hashes for the specified fetcher/source"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=10000)
        parser.add_argument("--async-reqs", type=int, default=3)

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

        for index, response in grequests.imap_enumerated(reqs, size=options["async_reqs"]):
            if response is None:
                # Failed downloading the image
                continue

            sauce = sauces[index]

            calc_hashes.delay(sauce.id, response.content, False)

            self.stdout.write(
                self.style.SUCCESS(f"ADDING")
                + f": {sauce.source_site_id} - {sauce.title}"
            )
