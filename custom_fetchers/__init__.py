def fetch_custom(source):

    fetcher = source["fetcher"]


    # ========================================================
    # EIGHTFOLD
    #
    # HSBC + BCG
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
    # BAIN
    # ========================================================

    if fetcher == "bain":

        from .bain import (
            fetch_bain
        )

        return fetch_bain(
            source
        )


    raise ValueError(
        f"Unknown custom fetcher: "
        f"{fetcher}"
    )
