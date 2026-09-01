from .bcg import fetch_bcg
from .avature import fetch_avature


def fetch_custom(source):
    """
    Route a custom source to the correct fetcher.
    """

    fetcher = source["fetcher"]

    if fetcher == "bcg":
        return fetch_bcg(source)

    if fetcher == "avature":
        return fetch_avature(source)

    raise ValueError(
        f"Unknown custom fetcher: {fetcher}"
    )
