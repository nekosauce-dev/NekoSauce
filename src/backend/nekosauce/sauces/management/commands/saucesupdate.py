import traceback
import multiprocessing

import grequests

from django.core.management.base import BaseCommand

from nekosauce.sauces.models import Sauce
from nekosauce.sauces.sources import get_fetcher, get_all_fetchers


def fetch_sauces(
    fetcher_class,
    async_reqs,
    chunk_size,
    limit,
    stdout,
    stderr,
    style,
):
    fetcher = fetcher_class(
        async_reqs=async_reqs,
    )
    source = fetcher.source

    stdout.write(f"\nFetching sauces from {source.name}")

    i = 0

    try:
        for sauce in fetcher.get_sauces_iter(
            chunk_size=chunk_size,
            start_from=fetcher.last_sauce,
        ):
            stdout.write(
                style.SUCCESS(f"ADDED")
                + f": ({source.name}) {sauce.source_site_id} - {sauce.title}"
            )

            i += 1
            if i >= limit:
                break
    except:
        stdout.write(
            style.ERROR(
                f"ERROR! Something went wrong fetching sauces from {source.name}."
            )
        )
        traceback.print_exc()


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
        fetchers = (
            get_all_fetchers() if source == "all" else [get_fetcher(source.lower())]
        )

        ps = []

        for fetcher_class in fetchers:
            p = multiprocessing.Process(
                target=fetch_sauces,
                args=(
                    fetcher_class,
                    async_reqs,
                    chunk_size,
                    limit,
                    self.stdout,
                    self.stderr,
                    self.style,
                ),
                daemon=True
            )
            p.start()
            ps.append(p)

        for p in ps:
            p.join()
