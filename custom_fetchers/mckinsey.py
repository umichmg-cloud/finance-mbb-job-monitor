import re
from urllib.parse import quote, urljoin

import requests
from bs4 import BeautifulSoup


REQUEST_TIMEOUT = 5


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/131.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


TARGET_LOCATIONS = {
    "Hong Kong SAR": [
        "hong kong",
    ],
    "Mexico City": [
        "mexico city",
        "ciudad de mexico",
        "ciudad de méxico",
    ],
}


# ============================================================
# KNOWN GLOBAL EARLY-CAREER MCKINSEY JOBS
#
# These provide a safe fallback if McKinsey's dynamic search
# page does not expose its result links to GitHub Actions.
# ============================================================

FALLBACK_JOBS = [

    {
        "id": "15136",
        "title": "Business Analyst",
        "location": (
            "Hong Kong SAR | Mexico City"
        ),
        "url": (
            "https://www.mckinsey.com/"
            "careers/search-jobs/jobs/"
            "businessanalyst-15136"
        ),
    },

    {
        "id": "15275",
        "title": "Business Analyst Intern",
        "location": "Hong Kong SAR",
        "url": (
            "https://www.mckinsey.com/"
            "careers/search-jobs/jobs/"
            "businessanalystintern-15275"
        ),
    },

]


def extract_job_id(url):

    match = re.search(
        r"-(\d+)(?:[/?#]|$)",
        url,
    )

    if match:
        return match.group(1)

    return ""


def title_from_url(url):

    slug = (
        url.rstrip("/")
        .split("/")[-1]
    )

    slug = re.sub(
        r"-\d+$",
        "",
        slug,
    )

    lower = slug.lower()


    if (
        "businessanalystintern"
        in lower
    ):
        return "Business Analyst Intern"


    if "businessanalyst" in lower:
        return "Business Analyst"


    return ""


def discover_jobs(
    session,
    search_url,
):
    """
    Search McKinsey by target city.

    IMPORTANT:
    We do NOT open each individual job page afterward.
    Those detail pages were timing out from GitHub Actions.

    Instead, the city search itself tells us which location
    exposed each job URL.
    """

    discovered = {}


    for location_name in TARGET_LOCATIONS:

        url = (
            search_url.rstrip("/")
            + "?cities="
            + quote(location_name)
        )


        try:

            response = session.get(
                url,
                timeout=REQUEST_TIMEOUT,
            )

            response.raise_for_status()

        except Exception as error:

            print(
                "  ⚠️ McKinsey search failed "
                f"for {location_name}: "
                f"{error}"
            )

            continue


        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )


        urls = set()


        # ----------------------------------------------------
        # NORMAL HTML LINKS
        # ----------------------------------------------------

        for anchor in soup.find_all(
            "a",
            href=True,
        ):

            absolute = urljoin(
                response.url,
                anchor["href"],
            )

            absolute = (
                absolute
                .split("?")[0]
            )


            if (
                "/careers/search-jobs/jobs/"
                not in absolute.lower()
            ):
                continue


            if (
                "businessanalyst"
                not in absolute.lower()
            ):
                continue


            urls.add(absolute)


        # ----------------------------------------------------
        # LINKS EMBEDDED IN SCRIPT / JSON
        # ----------------------------------------------------

        matches = re.findall(
            (
                r"""["']("""
                r"""[^"']*"""
                r"""/careers/search-jobs/jobs/"""
                r"""[^"'?#]+"""
                r""")["']"""
            ),
            response.text,
            flags=re.IGNORECASE,
        )


        for href in matches:

            absolute = urljoin(
                response.url,
                href,
            )

            absolute = (
                absolute
                .split("?")[0]
            )


            if (
                "businessanalyst"
                in absolute.lower()
            ):
                urls.add(absolute)


        # ----------------------------------------------------
        # SAVE WHERE EACH URL APPEARED
        # ----------------------------------------------------

        for job_url in urls:

            if job_url not in discovered:

                discovered[job_url] = {
                    "locations": set(),
                }


            discovered[
                job_url
            ]["locations"].add(
                location_name
            )


    return discovered


def fetch_mckinsey(source):

    session = requests.Session()

    session.headers.update(
        HEADERS
    )


    search_url = source["target"]


    discovered = discover_jobs(
        session,
        search_url,
    )


    print(
        "  McKinsey discovered URLs: "
        f"{len(discovered)}"
    )


    jobs_by_id = {}


    # ========================================================
    # DISCOVERED JOBS
    # ========================================================

    for url, metadata in (
        discovered.items()
    ):

        job_id = extract_job_id(url)

        title = title_from_url(url)


        if not job_id:
            continue


        if not title:
            continue


        locations = sorted(
            metadata["locations"]
        )


        if not locations:
            continue


        global_id = (
            f"mckinsey:{job_id}"
        )


        jobs_by_id[
            global_id
        ] = {

            "global_id":
                global_id,

            "title":
                title,

            "location":
                " | ".join(
                    locations
                ),

            "posted_at":
                "",

            "department":
                "Consulting",

            "team":
                "Generalist",

            "url":
                url,

            "apply_url":
                url,

        }


    # ========================================================
    # FALLBACK
    #
    # McKinsey sometimes hides search results behind
    # client-side rendering.
    #
    # We therefore retain known current global BA postings.
    # ========================================================

    for job in FALLBACK_JOBS:

        global_id = (
            f"mckinsey:{job['id']}"
        )


        if global_id in jobs_by_id:
            continue


        jobs_by_id[
            global_id
        ] = {

            "global_id":
                global_id,

            "title":
                job["title"],

            "location":
                job["location"],

            "posted_at":
                "",

            "department":
                "Consulting",

            "team":
                "Generalist",

            "url":
                job["url"],

            "apply_url":
                job["url"],

        }


    jobs = list(
        jobs_by_id.values()
    )


    print(
        "  McKinsey returned: "
        f"{len(jobs)} target roles"
    )


    return jobs
