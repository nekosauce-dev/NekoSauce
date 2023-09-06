from django.core.management.base import BaseCommand

from nekosauce.sauces.tasks import download_thumbnail
from nekosauce.sauces.models import Sauce


class Command(BaseCommand):
    help = "Updates all hashes for the specified fetcher/source"

    def add_arguments(self, parser):
        parser.add_argument("--limit", "-l", type=int, default=1000)
        parser.add_argument("--async-reqs", "-a", type=int, default=3)
        parser.add_argument("--chunk-size", "-c", type=int, default=128)

    def handle(self, *args, **options):
        self.stdout.write(f"Hashing sauces...")

        sauces = Sauce.objects.filter(sha512_hash__isnull=True)[: options["limit"]]
        reqs = []

        for sauce in sauces:
            download_thumbnail.send(sauce.id)

        self.stdout.write(self.style.SUCCESS("Done!"))
