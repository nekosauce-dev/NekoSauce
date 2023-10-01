from django.core.management.base import BaseCommand

from nekosauce.stats.models import Statistic
from nekosauce.sauces.models import (
    Sauce,
)


class Command(BaseCommand):
    help = "Update statistics"

    def handle(self, *args, **options):
        self.stdout.write("Updating statistics...")

        self.stdout.write("Counting sauces...")
        # TODO: Count sauces

        self.stdout.write("Counting hashes...")
        # TODO: Count sauces with hashes for each source

        self.stdout.write("Done!")
