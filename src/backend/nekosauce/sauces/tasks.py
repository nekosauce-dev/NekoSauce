import base64

import dramatiq

from nekosauce.sauces.models import Sauce


@dramatiq.actor
def calc_hashes(sauce_id: int, img_base64: str, replace: bool = False):
    img_bytes = base64.b64decode(img_base64.encode())
    sauce = Sauce.objects.get(id=sauce_id)
    sauce.calc_hashes(img_bytes)
