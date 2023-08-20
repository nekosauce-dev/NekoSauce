import time

from django.core.management.base import BaseCommand, CommandError

from nekosauce.sauces.models import Sauce
from nekosauce.sauces.sources import get_fetcher
from nekosauce.sauces.tasks import calc_hashes


class Command(BaseCommand):
    help = "Updates all hashes for the specified fetcher/source"

    def add_arguments(self, parser):
        parser.add_argument("--async-reqs", type=int, default=3)

    def handle(self, *args, **options):
        self.stdout.write(f"Hashing sauces...")

        for sauce in Sauce.objects.filter(downloaded=False).iterator():
            calc_hashes.delay(sauce.id, False)
            self.stdout.write(
                self.style.SUCCESS(f"ADDING")
                + f": {sauce.source_site_id} - {sauce.title}"
            )
