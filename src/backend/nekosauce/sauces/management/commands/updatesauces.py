import grequests

from django.db import transaction
from django.db.models import Q, F, IntegerField
from django.db.models.functions import Cast
from django.core.management.base import BaseCommand, CommandError

from nekosauce.sauces.utils import paginate
from nekosauce.sauces.tasks import calc_hashes
from nekosauce.sauces.models import Sauce, Source
from nekosauce.sauces.sources import get_fetcher, get_all_fetchers


class Command(BaseCommand):
    help = "Fetches new sauces for the specified fetcher/source"

    def add_arguments(self, parser):
        parser.add_argument("source", type=str, default="all")
        parser.add_argument("--async-reqs", "-a", type=int, default=3)
        parser.add_argument("--chunk-size", "-c", type=int, default=1024)
        parser.add_argument("--limit", "-l", type=int, default=100000)

    def handle(self, source, async_reqs=3, chunk_size=1024, limit=100000, *args, **options):
        fetchers = get_all_fetchers() if source == "all" else [get_fetcher(source.lower())]

        for fetcher_class in fetchers:
            fetcher = fetcher_class(
                async_reqs=async_reqs,
            )
            source = fetcher.source

            self.stdout.write(
                f"\nFetching sauces from {source.name}"
            )

            i = 0

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
