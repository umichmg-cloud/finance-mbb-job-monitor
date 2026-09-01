def fetch_custom(source):
    """
    Route custom job sources to the correct fetcher.
    """

    fetcher = source["fetcher"]


    # ========================================================
    # EIGHTFOLD
    #
    # HSBC
    # BCG
    # ========================================================

    if fetcher == "eightfold":

        from .eightfold import (
            fetch_eightfold
        )

        return fetch_eightfold(
            source
        )


    # ========================================================
    # MCKINSEY
    # ========================================================

    if fetcher == "mckinsey":

        from .mckinsey import (
            fetch_mckinsey
        )

        return fetch_mckinsey(
            source
        )


    # ========================================================
    # AVATURE
    #
    # Bain
    # ========================================================

    if fetcher == "avature":

        from .avature import (
            fetch_avature
        )

        return fetch_avature(
            source
        )


    # ========================================================
    # UNKNOWN
    # ========================================================

    raise ValueError(
        f"Unknown custom fetcher: "
        f"{fetcher}"
    )
