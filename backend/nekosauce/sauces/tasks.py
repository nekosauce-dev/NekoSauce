from celery import shared_task
from celery.utils.log import get_task_logger

from nekosauce.sauces.models import Sauce


logging = get_task_logger("nekosauce")


@shared_task
def calc_hashes(sauce_id: int, img_bytes: bytes, replace: bool = True):
    sauce = Sauce.objects.get(id=sauce_id)
    sauce.calc_hashes(img_bytes)


@shared_task
def update_sauces(source: str):
    from nekosauce.sauces.management.commands.updatesauces import Command
    Command().handle(source=source, async_reqs=3, start_from="last")


@shared_task
def update_hashes():
    from nekosauce.sauces.management.commands.updatehashes import Command
    Command().handle(limit=10000, async_reqs=3)
