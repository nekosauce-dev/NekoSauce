from celery import shared_task
from celery.utils.log import get_task_logger

from sauces.models import Sauce


logging = get_task_logger("nekosauce")


@shared_task
def calc_hashes(sauce_id: int, replace: bool = True):
    logging.info(f"Started calculating hashes for sauce: {sauce_id}")
    sauce = Sauce.objects.get(id=sauce_id)
    success, error_msg = sauce.calc_hashes()
    logging.info(f"Finished calculating hashes for sauce: {sauce_id}. Success: {success}")
