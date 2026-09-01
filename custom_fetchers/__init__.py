def fetch_custom(source):
    """
    Route custom sources to the correct fetcher.
    """

    fetcher = source["fetcher"]


    # ========================================================
    # EIGHTFOLD
    # ========================================================

    if fetcher == "eightfold":

        from .eightfold import (
            fetch_eightfold
        )

        return fetch_eightfold(
            source
        )


    # ========================================================
    # UNKNOWN
    # ========================================================

    raise ValueError(
        f"Unknown custom fetcher: {fetcher}"
    )
