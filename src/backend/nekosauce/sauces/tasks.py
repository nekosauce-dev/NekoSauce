import base64

import dramatiq

from nekosauce.sauces.models import Sauce


@dramatiq.actor
def calc_hashes(sauce_id: int, replace: bool = False):
    sauce = Sauce.objects.get(id=sauce_id)
    sauce.calc_hashes(img_bytes)
