import traceback
import subprocess

import grequests

from django.core.management.base import BaseCommand

from nekosauce.sauces.models import Sauce
from nekosauce.sauces.sources import get_fetcher, get_all_fetchers


class Command(BaseCommand):
    help = "Fetches new sauces for the specified fetcher/source"

    def add_arguments(self, parser):
        parser.add_argument("--source", type=str, default="all")
        parser.add_argument("--async-reqs", "-a", type=int, default=3)
        parser.add_argument("--chunk-size", "-c", type=int, default=1024)
        parser.add_argument("--limit", "-l", type=int, default=100000)

    def handle(
        self, source, async_reqs=3, chunk_size=1024, limit=100000, *args, **options
    ):
        if source == "all":
            sources = get_all_fetchers()

            ps = []

            for source in sources:
                ps.append(subprocess.Popen("python3 manage.py saucesupdate --source \"%s\" --async-reqs %s --chunk-size %s --limit %s" % (
                    source,
                    async_reqs,
                    chunk_size,
                    limit
                )))
            
            for p in ps:
                p.wait()

            return

        fetcher = get_fetcher(source.lower())(
            async_reqs=async_reqs,
        )
        source = fetcher.source

        self.stdout.write(f"\nFetching sauces from {source.name}")

        i = 0

        try:
            for sauce in fetcher.get_sauces_iter(
                chunk_size=chunk_size,
                start_from=fetcher.last_sauce,
            ):
                self.stdout.write(
                    self.style.SUCCESS(f"ADDED")
                    + f": ({source.name}) {sauce.source_site_id} - {sauce.title}"
                )

                i += 1
                if i >= limit:
                    break
        except:
            self.stdout.write(
                self.style.ERROR(
                    f"ERROR! Something went wrong fetching sauces from {source.name}."
                )
            )
            traceback.print_exc()
