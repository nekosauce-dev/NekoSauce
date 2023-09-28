import os

from django.core.management.base import BaseCommand, CommandError

import requests

from nekosauce.sauces.models import Sauce, Hash, Source


def format_large_number(number):
    return "{:,}".format(number)


class Command(BaseCommand):
    help = "Posts database update to Discord channel"

    def handle(self, *args, **options):
        new_line = "\n"

        self.stdout.write("Sending update (it can take a few seconds)...")

        r = requests.post(
            os.getenv("BACKEND_DISCORD_DATABASE_UPDATES_WEBHOOK_URL"),
            json={
                "content": (
                    "__**NekoSauce Database Update!**__\n\n"
                    f"Sauces: {format_large_number(Sauce.objects.count())}" + "\n"
                    f"Hashes: {format_large_number(Hash.objects.count())}" + "\n\n"
                    "**Which sources?**\n"
                    f"{new_line.join([f'- {source.name}: {format_large_number(source.sauces.count())}' for source in Source.objects.filter(enabled=True).order_by('id')])}"
                    "\n\n------\n\n"
                    "This update is automatic. NekoSauce will be released once the hashes amount matches (or almost matches) the amount of sauces."
                )
            },
        )
        r.raise_for_status()

        self.stdout.write("Update posted!")
