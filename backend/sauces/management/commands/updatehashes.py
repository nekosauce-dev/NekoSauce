import time

from django.core.management.base import BaseCommand, CommandError

from sauces.models import Sauce
from sauces.sources import get_fetcher
from sauces.tasks import calc_hashes


class Command(BaseCommand):
    help = "Updates all hashes for the specified fetcher/source"

    def add_arguments(self, parser):
        parser.add_argument("--async-reqs", type=int, default=3)

    def handle(self, *args, **options):
        self.stdout.write(f"Hashing sauces...")

        for sauce in Sauce.objects.filter(downloaded=False)[:1000]:
            calc_hashes.delay(sauce.id, False)
            self.stdout.write(self.style.SUCCESS(f"ADDING") + f": {sauce.source_site_id} - {sauce.title}")
