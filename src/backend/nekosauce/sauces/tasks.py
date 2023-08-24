from celery import shared_task
from celery.utils.log import get_task_logger

from nekosauce.sauces.models import Sauce


logging = get_task_logger("nekosauce")


@shared_task
def calc_hashes(sauce_id: int, img_bytes: bytes, replace: bool = True):
    sauce = Sauce.objects.get(id=sauce_id)
    sauce.calc_hashes(img_bytes)


@shared_task
def update_sauces(async_reqs=3, chunk_size=1024):
    from nekosauce.sauces.management.commands.updatesauces import Command
    Command().handle(async_reqs=async_reqs, chunk_size=chunk_size)


@shared_task
def update_hashes(limit=10000, async_reqs=3, chunk_size=128):
    from nekosauce.sauces.management.commands.updatehashes import Command
    Command().handle(limit=limit, async_reqs=async_reqs, chunk_size=chunk_size)
