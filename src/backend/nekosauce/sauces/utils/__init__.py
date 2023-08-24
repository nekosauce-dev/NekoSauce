def paginate(iterable, limit: int) -> list:
    return [(iterable[i : i + limit], i) for i in range(0, len(iterable), limit)]
