import jstyleson


registry = jstyleson.load(open("registry.jsonc", "r"))


def get_sauce_type(id: int) -> str:
    for sauce in registry["sauce_types"]:
        if sauce["id"] == id:
            return sauce
