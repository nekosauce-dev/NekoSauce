from django.db.models import Q, F, IntegerField
from django.db.models.functions import Cast
from django.core.management.base import BaseCommand, CommandError

from sauces.models import Sauce, Artist, Source
from sauces.sources import get_fetcher


class Command(BaseCommand):
    help = "Fetches new sauces for the specified fetcher/source"

    def add_arguments(self, parser):
        parser.add_argument("fetcher", type=str)
        parser.add_argument("--start-from", type=str)

    def handle(self, *args, **options):
        fetcher_class = get_fetcher(options["fetcher"].lower())

        if fetcher_class is None:
            raise CommandError(f"Invalid fetcher: {options['fetcher']}")

        start_from = 0
        if options.get("start_from", "0") == "last":
            last_sauce = (
                Sauce.objects.annotate(
                    numeric_id=Cast(F("source_site_id"), output_field=IntegerField())
                )
                .order_by("numeric_id")
                .first()
            )
            start_from = f"b{last_sauce.source_site_id}"
        else:
            start_from = (
                int(options.get("start_from", "0"))
                if options.get("start_from", "0") is not None
                and options.get("start_from", "0").isnumeric()
                else options.get("start_from", 0)
                if options.get("start_from", 0)
                else 0
            )

        fetcher = fetcher_class(
            iter_from=start_from,
            async_reqs=10,
        )
        source = Source.objects.get(name__iexact=options["fetcher"])

        self.stdout.write(
            f"Fetching sauces from {source.name}"
            + (f", starting from page {start_from}" if start_from else "")
        )

        for sauce in fetcher:
            self.stdout.write(
                self.style.SUCCESS(f"ADDED")
                + f": {sauce.source_site_id} - {sauce.title}"
            )
