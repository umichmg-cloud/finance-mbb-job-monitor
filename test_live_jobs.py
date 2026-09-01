from ats_scrapers import get_scraper_for_url
from ats_scrapers.scrapers import get_scraper

from sources import SOURCES


# ============================================================
# TARGET LOCATIONS
# ============================================================

TARGET_LOCATIONS = [
    # Hong Kong
    "hong kong",
    "hongkong",
    "hong kong sar",
    "hong kong s.a.r",
    "hksar",

    # Mexico City
    "mexico city",
    "ciudad de mexico",
    "ciudad de méxico",
    "cdmx",
    "mexico d.f",
    "mexico, df",
]


def get_value(job, field):
    """
    Safely retrieve a field from the Job object.
    """

    value = getattr(job, field, None)

    if value is None:
        return ""

    return str(value)


def is_target_location(job):
    """
    Check both location and description.

    We check description too because graduate programs
    sometimes list several eligible cities in the job text
    while the ATS only gives one primary location.
    """

    location = get_value(job, "location")
    description = get_value(job, "description")

    searchable_text = (
        location + " " + description[:8000]
    ).lower()

    return any(
        term.lower() in searchable_text
        for term in TARGET_LOCATIONS
    )


def create_scraper(source):
    """
    Create the correct ats-scrapers scraper.

    Some companies are identified directly by ATS + slug.
    Others are resolved using their official careers URL.
    """

    if source["method"] == "ats":

        return get_scraper(
            source["ats"],
            source["slug"],
        )

    if source["method"] == "url":

        return get_scraper_for_url(
            source["url"]
        )

    raise ValueError(
        f"Unknown source method: {source['method']}"
    )


print()
print("=" * 90)
print("LIVE JOB SOURCE TEST")
print("TARGET: HONG KONG + MEXICO CITY")
print("=" * 90)


summary = []


for source in SOURCES:

    company = source["name"]

    print()
    print()
    print("=" * 90)
    print(f"TESTING: {company}")
    print("=" * 90)

    try:

        # --------------------------------------------------------
        # CREATE SCRAPER
        # --------------------------------------------------------

        scraper = create_scraper(source)

        print("✅ Scraper created")

        # --------------------------------------------------------
        # FETCH LIVE JOBS
        # --------------------------------------------------------

        jobs = scraper.fetch()

        print(
            f"✅ Retrieved {len(jobs)} total live jobs"
        )

        # --------------------------------------------------------
        # FIND HK / CDMX JOBS
        # --------------------------------------------------------

        target_jobs = [
            job
            for job in jobs
            if is_target_location(job)
        ]

        print(
            f"📍 Hong Kong / Mexico City matches: "
            f"{len(target_jobs)}"
        )

        summary.append(
            (
                company,
                "OK",
                len(jobs),
                len(target_jobs),
            )
        )

        # --------------------------------------------------------
        # SHOW UP TO 15 MATCHES
        # --------------------------------------------------------

        if target_jobs:

            print()
            print("MATCHING JOBS:")
            print("-" * 90)

            for number, job in enumerate(
                target_jobs[:15],
                start=1,
            ):

                title = get_value(job, "title")
                location = get_value(job, "location")
                posted = get_value(job, "posted_at")

                apply_url = (
                    get_value(job, "apply_url")
                    or get_value(job, "url")
                )

                print()
                print(f"{number}. {title}")
                print(f"   Location: {location}")

                if posted:
                    print(f"   Posted: {posted}")

                print(f"   URL: {apply_url}")

        else:

            print(
                "ℹ️ Source works, but no HK/CDMX "
                "roles were detected."
            )

    except Exception as error:

        print()
        print("❌ SOURCE FAILED")
        print(
            f"{type(error).__name__}: {error}"
        )

        summary.append(
            (
                company,
                "FAILED",
                0,
                0,
            )
        )


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print()
print("=" * 90)
print("FINAL SUMMARY")
print("=" * 90)

for company, status, total, target in summary:

    symbol = "✅" if status == "OK" else "❌"

    print(
        f"{symbol} "
        f"{company:<25} "
        f"total={total:<6} "
        f"HK/CDMX={target}"
    )

print()
print("=" * 90)
print("TEST FINISHED")
print("=" * 90)
