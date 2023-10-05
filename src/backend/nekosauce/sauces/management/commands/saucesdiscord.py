import os

from django.core.management.base import BaseCommand, CommandError

import requests

from nekosauce.stats.models import Statistic
from nekosauce.sauces.models import Sauce
from nekosauce.sauces.utils.registry import registry


def format_large_number(number):
    return "{:,}".format(number)


def modification(old, new) -> str:
    return (
        (
            (
                # The - will be added when the subtraction returns a negative number
                "+"
                if new > old
                else ""
            )
            + format_large_number(new - old)
        )
        if old != new
        else "N/A"
    )


class Command(BaseCommand):
    help = "Posts database update to Discord channel"

    def handle(self, *args, **options):
        new_line = "\n"

        self.stdout.write("Sending update (it can take a few seconds)...")

        sources = [
            {
                "id": source["id"],
                "name": source["name"],
                "link": source["urls"]["website"],
                "last_sauce_count": getattr(
                    Statistic.objects.filter(
                        resource="Sauce",
                        attribute="total-count:source_id={}".format(source["id"]),
                    )
                    .order_by("created_at")
                    .last(),
                    "value",
                    0,
                ),
                "last_hash_count": getattr(
                    Statistic.objects.filter(
                        resource="Sauce",
                        attribute="processed-count:source_id={}".format(source["id"]),
                    )
                    .order_by("created_at")
                    .last(),
                    "value",
                    0,
                ),
            }
            for source in registry["sources"]
            if source["enabled"] and source["components"]["fetcher"]
        ]

        def stats(source: int) -> str:
            total_count = Sauce.objects.filter(source_id=source[0]).count()
            processed_count = Sauce.objects.filter(
                source_id=source["id"], hash__isnull=False
            ).count()

            processed_percentage = (
                processed_count / total_count * 100 if total_count > 0 else 0.0
            )
            precentage_display = "{:.2f}".format(processed_percentage)

            Statistic.objects.create(
                resource="Sauce",
                attribute="total-count:source_id={}".format(source["id"]),
                value=total_count,
            )
            Statistic.objects.create(
                resource="Sauce",
                attribute="processed-count:source_id={}".format(source["id"]),
                value=processed_count,
            )

            return f"- {source['id']}: {format_large_number(total_count)}s ({format_large_number(processed_count)}h, {precentage_display}%, {modification(source['last_sauce_count'], total_count)})"

        current_total = Sauce.objects.count()
        current_processed = Sauce.objects.filter(hash__isnull=False).count()

        last_total = sum([source["last_count"] for source in sources])
        last_processed = sum([source["last_processed"] for source in sources])

        r = requests.post(
            os.getenv("BACKEND_DISCORD_DATABASE_UPDATES_WEBHOOK_URL"),
            json={
                "content": (
                    "__**NekoSauce Database Update!**__\n\n"
                    f"Sauces: {format_large_number(current_total)} ({modification(last_total, current_total)})"
                    + "\n"
                    f"Hashes: {format_large_number(current_processed)} ({modification(last_processed, current_processed)})"
                    + "\n\n"
                    "**Which sources?**\n"
                    f"{new_line.join(map(stats, sources))}\n\n"
                    "Note: __s__ are sauces, __h__ are hashes\n\n"
                    "------\n\n"
                    "This update is automatic. NekoSauce will be released once the hashes amount matches (or almost matches) the amount of sauces."
                )
            },
        )
        r.raise_for_status()

        self.stdout.write("Update posted!")
