import base64

import dramatiq

from nekosauce.sauces.models import Sauce


@dramatiq.actor
def calc_hash(sauce_id: int):
    try:
        sauce = Sauce.objects.get(id=sauce_id)
        sauce.calc_hash(save=True)
    except Exception as e:
        print("Worker raised an error.")
        print(e)


@dramatiq.actor
def download_thumbnail(sauce_id: int):
    try:
        sauce = Sauce.objects.get(id=sauce_id)
        sauce.download_thumbnail()
    except Exception as e:
        print("Worker raised an error.")
        print(e)
