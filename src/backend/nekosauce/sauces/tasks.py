import base64

import dramatiq

from nekosauce.sauces.models import Sauce


def get_or_none(klass, **kwargs):
    """Gets the first object matching the given kwargs, or None if it does not
    exist.

    Args:
        klass (Model): The model class to get.

    Returns:
        Model?: The instance of the model, or None if it does not exist.
    """

    try:
        return klass.objects.get(**kwargs)
    except klass.DoesNotExist:
        return None


@dramatiq.actor(max_retries=3)
def sauce_process(sauce_id: int):
    sauce = get_or_none(Sauce, id=sauce_id)
    
    if sauce is not None:
        try:
            success, msg = sauce.process(save=True)
            if not success and msg:
                raise Exception(msg)
        except Exception as e:
            sauce.status = Sauce.Status.FAILED
            sauce.save()
            
            print("Worker raised an error.")
            print(e)
