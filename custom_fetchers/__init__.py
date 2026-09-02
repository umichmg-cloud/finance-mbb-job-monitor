def fetch_custom(source):
    """
    Route custom sources to the correct fetcher.
    """

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


    # ========================================================
    # TAL.NET
    #
    # Bank of America
    # Evercore
    # Rothschild & Co
    # ========================================================

    if fetcher == "talnet":

        from .talnet import (
            fetch_talnet
        )

        return fetch_talnet(
            source
        )


    # ========================================================
    # BRASSRING
    #
    # UBS
    # ========================================================

    if fetcher == "brassring":

        from .brassring import (
            fetch_brassring
        )

        return fetch_brassring(
            source
        )


    # ========================================================
    # YELLO
    #
    # Deutsche Bank
    # ========================================================

    if fetcher == "yello":

        from .yello import (
            fetch_yello
        )

        return fetch_yello(
            source
        )


    # ========================================================
    # AVATURE
    #
    # Macquarie
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
