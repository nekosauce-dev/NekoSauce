from django.core.management.base import BaseCommand

from nekosauce.stats.models import Statistic
from nekosauce.sauces.models import Sauce, Source, Hash, Hash8Bits, Hash16Bits, Hash32Bits, Hash64Bits


class Command(BaseCommand):
    help = 'Update statistics'

    def handle(self, *args, **options):
        self.stdout.write("Updating statistics...")

        self.stdout.write("Counting sauces...")
        Statistic.objects.create(
            resource="sauce:danbooru",
            attribute="count",
            value=Sauce.objects.filter(source=Source.objects.get(name__iexact="danbooru")).count(),
        )
        Statistic.objects.create(
            resource="sauce:gelbooru",
            attribute="count",
            value=Sauce.objects.filter(source=Source.objects.get(name__iexact="gelbooru")).count(),
        )

        self.stdout.write("Counting hashes...")
        for hash_model in [Hash8Bits, Hash16Bits, Hash32Bits, Hash64Bits]:
            for i in range(len(Hash.Algorithm)):
                Statistic.objects.create(
                    resource="hash:{}:{}".format(hash_model.__name__.lower()[4:], Hash.Algorithm._value2member_map_[i]),
                    attribute="count",
                    value=hash_model.objects.filter(algorithm=Hash.Algorithm._value2member_map_[i]).count(),
                )

        self.stdout.write("Done!")
