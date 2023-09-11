from django.db.models import Q
from django.core.management.base import BaseCommand

from nekosauce.sauces.tasks import sauce_process
from nekosauce.sauces.models import Sauce


class Command(BaseCommand):
    help = "Updates all hashes for the specified fetcher/source"

    def add_arguments(self, parser):
        parser.add_argument("--limit", "-l", type=int, default=1000)

    def handle(self, *args, **options):
        self.stdout.write(f"Processing sauces...")

        sauces = Sauce.objects.filter(Q(hash__isnull=True) | Q(sha512_hash__isnull=True))[: options["limit"]]
        reqs = []

        for sauce in sauces:
            sauce_process.send(sauce.id)

        self.stdout.write(self.style.SUCCESS("Done!"))
