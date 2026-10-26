from werkzeug.routing import IntegerConverter

MAX_ID = 2**63 - 1


class IdConverter(IntegerConverter):
    def __init__(self, url_map):
        super().__init__(url_map, min=1, max=MAX_ID)


def parse_id(value):
    number = int(value)
    if not 1 <= number <= MAX_ID:
        raise ValueError("Identifiant hors limites.")
    return number
