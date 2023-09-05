import base64

import dramatiq

from nekosauce.sauces.models import Sauce


@dramatiq.actor
def calc_hashes(sauce_id: int):
    try:
        sauce = Sauce.objects.get(id=sauce_id)
        try:
            sauce.calc_hashes(save=True)
        except:
            sauce.downloaded = Null
            sauce.save()
    except:
        print("Worker raised an error.")
