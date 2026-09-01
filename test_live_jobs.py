from ats_scrapers.scrapers import get_scraper

from sources import SOURCES


# ============================================================
# LOCATION MATCHING
# ============================================================
#
# IMPORTANT:
#
# We ONLY use the structured location field here.
#
# Previously we searched the description as well.
# That caused false positives:
#
# New York jobs were being classified as Hong Kong jobs
# simply because their description happened to mention HK.
#
# ============================================================


HONG_KONG_TERMS = [
    "hong kong",
    "hongkong",
    "hong kong sar",
    "hong kong s.a.r",
]


MEXICO_CITY_TERMS = [
    "mexico city",
    "ciudad de mexico",
    "ciudad de méxico",
    "cdmx",
    "mexico d.f",
    "mexico, df",
    "mexico city, mexico",
]


def get_value(job, field):
    """
    Safely retrieve a value from an ats-scrapers Job object.
    """

    value = getattr(job, field, None)

    if value is None:
        return ""

    return str(value).strip()


def classify_location(job):
    """
    Return:
        "Hong Kong"
        "Mexico City"
        None

    We intentionally examine ONLY job.location.
    """

    location = get_value(
        job,
        "location",
    ).lower().strip()

    # --------------------------------------------------------
    # HONG KONG
    # --------------------------------------------------------

    # Morgan Stanley, for example, often simply returns "HK".
    if location == "hk":
        return "Hong Kong"

    if any(
        term in location
        for term in HONG_KONG_TERMS
    ):
        return "Hong Kong"

    # --------------------------------------------------------
    # MEXICO CITY
    # --------------------------------------------------------

    if any(
        term in location
        for term in MEXICO_CITY_TERMS
    ):
        return "Mexico City"

    return None


# ============================================================
# SCRAPER CREATION
# ============================================================


def create_scraper(source):
    """
    Create the appropriate scraper from our manually
    verified ATS + target pair.
    """

    return get_scraper(
        source["ats"],
        source["target"],
    )


# ============================================================
# TEST
# ============================================================


print()
print("=" * 100)
print("LIVE FINANCE JOB SOURCE TEST")
print("LOCATIONS: HONG KONG + MEXICO CITY")
print("=" * 100)


summary = []


for source in SOURCES:

    company = source["name"]

    print()
    print()
    print("=" * 100)
    print(f"TESTING: {company}")
    print(f"ATS: {source['ats']}")
    print("=" * 100)

    try:

        # ----------------------------------------------------
        # CREATE SCRAPER
        # ----------------------------------------------------

        scraper = create_scraper(source)

        print("✅ Scraper created")


        # ----------------------------------------------------
        # FETCH JOBS
        # ----------------------------------------------------

        jobs = scraper.fetch()

        total_jobs = len(jobs)

        print(
            f"✅ Retrieved {total_jobs} total live jobs"
        )


        # ----------------------------------------------------
        # ZERO JOBS IS SUSPICIOUS
        # ----------------------------------------------------

        if total_jobs == 0:

            print()
            print(
                "⚠️ WARNING: scraper returned ZERO jobs."
            )

            print(
                "We will treat this source as unresolved "
                "rather than assuming the company has no jobs."
            )

            summary.append(
                (
                    company,
                    "EMPTY",
                    0,
                    0,
                    0,
                )
            )

            continue


        # ----------------------------------------------------
        # LOCATION FILTER
        # ----------------------------------------------------

        hong_kong_jobs = []
        mexico_city_jobs = []


        for job in jobs:

            location_group = classify_location(job)

            if location_group == "Hong Kong":

                hong_kong_jobs.append(job)

            elif location_group == "Mexico City":

                mexico_city_jobs.append(job)


        target_jobs = (
            hong_kong_jobs
            +
            mexico_city_jobs
        )


        print()
        print(
            f"🇭🇰 Hong Kong jobs: "
            f"{len(hong_kong_jobs)}"
        )

        print(
            f"🇲🇽 Mexico City jobs: "
            f"{len(mexico_city_jobs)}"
        )

        print(
            f"📍 Total target-location jobs: "
            f"{len(target_jobs)}"
        )


        summary.append(
            (
                company,
                "OK",
                total_jobs,
                len(hong_kong_jobs),
                len(mexico_city_jobs),
            )
        )


        # ----------------------------------------------------
        # DISPLAY TARGET JOBS
        # ----------------------------------------------------

        if target_jobs:

            print()
            print("TARGET-LOCATION JOBS:")
            print("-" * 100)


            for number, job in enumerate(
                target_jobs[:25],
                start=1,
            ):

                title = get_value(
                    job,
                    "title",
                )

                location = get_value(
                    job,
                    "location",
                )

                posted = get_value(
                    job,
                    "posted_at",
                )

                url = (
                    get_value(
                        job,
                        "apply_url",
                    )
                    or
                    get_value(
                        job,
                        "url",
                    )
                )

                print()
                print(
                    f"{number}. {title}"
                )

                print(
                    f"   Location: {location}"
                )

                if posted:

                    print(
                        f"   Posted: {posted}"
                    )

                print(
                    f"   URL: {url}"
                )


        else:

            print()
            print(
                "ℹ️ The scraper works, but it returned "
                "no jobs whose structured location is "
                "Hong Kong or Mexico City."
            )


    except Exception as error:

        print()
        print("❌ SOURCE FAILED")

        print(
            f"{type(error).__name__}: "
            f"{error}"
        )

        summary.append(
            (
                company,
                "FAILED",
                0,
                0,
                0,
            )
        )


# ============================================================
# FINAL SUMMARY
# ============================================================


print()
print()
print("=" * 100)
print("FINAL SUMMARY")
print("=" * 100)


for (
    company,
    status,
    total,
    hk,
    mexico,
) in summary:

    if status == "OK":
        symbol = "✅"

    elif status == "EMPTY":
        symbol = "⚠️"

    else:
        symbol = "❌"


    print(
        f"{symbol} "
        f"{company:<23} "
        f"total={total:<6} "
        f"HK={hk:<4} "
        f"CDMX={mexico:<4} "
        f"status={status}"
    )


print()
print("=" * 100)
print("TEST FINISHED")
print("=" * 100)
