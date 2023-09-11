import base64

import dramatiq

from nekosauce.sauces.models import Sauce


@dramatiq.actor(max_retries=0)
def sauce_process(sauce_id: int):
    try:
        sauce = Sauce.objects.get(id=sauce_id)
        sauce.process(save=True)
    except Exception as e:
        print("Worker raised an error.")
        print(e)
