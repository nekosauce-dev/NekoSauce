import grequests

from django.db import transaction
from django.db.models import Q, F, IntegerField
from django.db.models.functions import Cast
from django.core.management.base import BaseCommand, CommandError

from nekosauce.sauces.sources import get_all_fetchers
from nekosauce.sauces.models import Sauce, Source
from nekosauce.sauces.tasks import calc_hashes


class Command(BaseCommand):
    help = "Fetches new sauces for the specified fetcher/source"

    def add_arguments(self, parser):
        parser.add_argument("--async-reqs", type=int, default=3)

    def handle(self, *args, **options):
        for fetcher_class in get_all_fetchers():
            fetcher = fetcher_class(
                async_reqs=options["async_reqs"],
            )
            source = fetcher.source

            self.stdout.write(
                f"\nFetching sauces from {source.name}"
            )

            loaded_ids = []

            for sauce in fetcher.get_sauces_iter(
                start_from=fetcher.last_sauce,
            ):
                if sauce.source_site_id in loaded_ids:
                    break

                loaded_ids.append(sauce.source_site_id)
                self.stdout.write(
                    self.style.SUCCESS(f"ADDED")
                    + f": ({source.name}) {sauce.source_site_id} - {sauce.title}"
                )
