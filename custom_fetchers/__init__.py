def fetch_custom(source):
    """
    Route a custom job source to the appropriate fetcher.

    Each custom fetcher must return a list of dictionaries
    using the normalized fields expected by monitor.py.
    """

    fetcher = source["fetcher"]


    # ========================================================
    # MCKINSEY
    # ========================================================

    if fetcher == "mckinsey":

        from .mckinsey import fetch_mckinsey

        return fetch_mckinsey(source)


    # ========================================================
    # BCG
    # ========================================================

    if fetcher == "bcg":

        from .bcg import fetch_bcg

        return fetch_bcg(source)


    # ========================================================
    # AVATURE
    #
    # Currently used for Bain.
    # Later it can support other Avature employers too.
    # ========================================================

    if fetcher == "avature":

        from .avature import fetch_avature

        return fetch_avature(source)


    # ========================================================
    # UNKNOWN FETCHER
    # ========================================================

    raise ValueError(
        f"Unknown custom fetcher: {fetcher}"
    )
