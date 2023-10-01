import jstyleson


registry = jstyleson.load(open("registry.jsonc", "r"))


def get_sauce_type(id: int) -> str:
    for sauce in registry["sauce_types"]:
        if sauce["id"] == id:
            return sauce


def get_sauce_type_by_name(name: str):
    for sauce in registry["sauce_types"]:
        if sauce["name"].lower() == name.lower():
            return sauce


def get_source(id: int):
    for source in registry["sources"]:
        if source["id"] == id:
            return source


def get_source_by_name(name: str):
    for source in registry["sources"]:
        if source["name"].lower() == name.lower():
            return source
