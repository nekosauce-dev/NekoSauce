import time
import base64

from django.core.management.base import BaseCommand, CommandError

import grequests

from nekosauce.sauces.utils import paginate
from nekosauce.sauces.tasks import calc_hashes
from nekosauce.sauces.models import Sauce
from nekosauce.sauces.sources import get_downloader


class Command(BaseCommand):
    help = "Updates all hashes for the specified fetcher/source"

    def add_arguments(self, parser):
        parser.add_argument("--limit", "-l", type=int, default=1000)
        parser.add_argument("--async-reqs", "-a", type=int, default=3)
        parser.add_argument("--chunk-size", "-c", type=int, default=128)

    def handle(self, *args, **options):
        self.stdout.write(f"Hashing sauces...")

        sauces = Sauce.objects.filter(downloaded=False)[: options["limit"]]
        reqs = []

        for sauce in sauces:
            calc_hashes.send(sauce.id)

        self.stdout.write(self.style.SUCCESS("Done!"))
