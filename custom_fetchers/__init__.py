def fetch_custom(source):
    """
    Route custom job sources to their fetchers.

    Normal ATS sources continue to use ats-scrapers.
    Only sources with method="custom" arrive here.
    """

    fetcher = source["fetcher"]


    # ========================================================
    # BOSTON CONSULTING GROUP
    # ========================================================

    if fetcher == "bcg":

        from .bcg import fetch_bcg

        return fetch_bcg(source)


    # ========================================================
    # UNKNOWN CUSTOM SOURCE
    # ========================================================

    raise ValueError(
        f"Unknown custom fetcher: {fetcher}"
    )
