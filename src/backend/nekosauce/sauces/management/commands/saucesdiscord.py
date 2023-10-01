import os

from django.core.management.base import BaseCommand, CommandError

import requests

from nekosauce.sauces.models import Sauce
from nekosauce.sauces.utils.registry import registry


def format_large_number(number):
    return "{:,}".format(number)


class Command(BaseCommand):
    help = "Posts database update to Discord channel"

    def handle(self, *args, **options):
        new_line = "\n"

        self.stdout.write("Sending update (it can take a few seconds)...")

        sources = [
            (source["id"], source["name"]) for source in registry["sources"] if source["enabled"]
        ]

        r = requests.post(
            os.getenv("BACKEND_DISCORD_DATABASE_UPDATES_WEBHOOK_URL"),
            json={
                "content": (
                    "__**NekoSauce Database Update!**__\n\n"
                    f"Sauces: {format_large_number(Sauce.objects.count())}" + "\n"
                    f"Hashes: {format_large_number(Sauce.objects.filter(hash__isnull=False).count())}" + "\n\n"
                    "**Which sources?**\n"
                    f"{new_line.join([f'- {source[1]}: {format_large_number(Sauce.objects.filter(source_id={source[0]}).count())}' for source in sources])}"
                    "\n\n------\n\n"
                    "This update is automatic. NekoSauce will be released once the hashes amount matches (or almost matches) the amount of sauces."
                )
            },
        )
        r.raise_for_status()

        self.stdout.write("Update posted!")
