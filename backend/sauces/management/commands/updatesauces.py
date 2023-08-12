from django.db.models import Q
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

        fetcher = fetcher_class(
            iter_from=int(options.get("start_from", "0"))
            if options.get("start_from", "0") is not None
            and options.get("start_from", "0").isnumeric()
            else options.get("start_from", 0),
            async_reqs=10,
        )
        source = Source.objects.get(name__iexact=options["fetcher"])

        self.stdout.write(
            f"Fetching sauces from {source.name}, starting from page {options.get('start_from', '0')}"
        )

        for sauce in fetcher:
            artist: Artist

            if sauce.artist is not None:
                try:
                    artist = Artist.objects.get(
                        Q(api_urls__overlap=sauce.artist.api_urls)
                        | Q(site_urls__overlap=sauce.site_urls),
                        names__overlap=sauce.artist.names,
                    )
                except Artist.DoesNotExist:
                    artist = Artist.objects.create(
                        names=sauce.artist.names,
                        site_urls=sauce.site_urls,
                        api_urls=sauce.artist.api_urls,
                    )

            instance = Sauce(
                file_url=sauce.file_url,
                site_urls=sauce.site_urls,
                api_urls=sauce.api_urls,
                sauce_type=sauce.sauce_type.value,
                title=f"{sauce.sauce_type.value.title()} on {sauce.sauce_name} - {sauce.file_url.rsplit('/', 1)[1]}",
                site_id=str(sauce.sauce_site_id),
                width=sauce.width,
                height=sauce.height,
                artist=artist,
                source=source,
            )
            instance.save()

            self.stdout.write(
                self.style.SUCCESS(f"ADDED")
                + f": {sauce.sauce_site_id} - {instance.title}"
            )
