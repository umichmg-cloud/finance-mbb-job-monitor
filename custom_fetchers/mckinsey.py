import re
from urllib.parse import quote, urljoin

import requests
from bs4 import BeautifulSoup


REQUEST_TIMEOUT = 30

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


TARGET_LOCATIONS = [
    "Hong Kong SAR",
    "Mexico City",
]


# ============================================================
# STABLE MCKINSEY EARLY-CAREER POSTINGS
# ============================================================
#
# McKinsey uses global job postings that may contain many
# office locations.
#
# These are also used as a fallback if the dynamic search page
# does not expose its result links in server-rendered HTML.
# ============================================================

SEED_JOBS = [

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


def _get(session, url):
    response = session.get(
        url,
        timeout=REQUEST_TIMEOUT,
        allow_redirects=True,
    )

    response.raise_for_status()

    return response


def _job_id(url):
    match = re.search(
        r"-(\d+)(?:[/?#]|$)",
        url,
    )

    if match:
        return match.group(1)

    return ""


def _target_location(text):
    lower = text.lower()

    locations = []


    if "hong kong" in lower:

        locations.append(
            "Hong Kong SAR"
        )


    if (
        "mexico city" in lower
        or "ciudad de mexico" in lower
        or "ciudad de méxico" in lower
    ):

        locations.append(
            "Mexico City"
        )


    return " | ".join(
        locations
    )


def _discover_urls(
    session,
    search_url,
):
    """
    Try McKinsey's own filtered search pages.

    If McKinsey exposes job links in the HTML, this lets us
    discover new Business Analyst postings automatically.

    If the site is fully client-rendered, SEED_JOBS remains
    the fallback.
    """

    urls = set()


    for city in TARGET_LOCATIONS:

        url = (
            search_url.rstrip("/")
            + "?cities="
            + quote(city)
        )


        try:

            response = _get(
                session,
                url,
            )

        except Exception:

            continue


        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )


        # ----------------------------------------------------
        # NORMAL LINKS
        # ----------------------------------------------------

        for anchor in soup.find_all(
            "a",
            href=True,
        ):

            absolute = urljoin(
                response.url,
                anchor["href"],
            )

            lower = absolute.lower()


            if (
                "/careers/search-jobs/jobs/"
                in lower
                and "businessanalyst"
                in lower
            ):

                urls.add(
                    absolute.split("?")[0]
                )


        # ----------------------------------------------------
        # LINKS EMBEDDED IN JAVASCRIPT / JSON
        # ----------------------------------------------------

        for href in re.findall(
            r"""["']([^"']*/careers/search-jobs/jobs/[^"'?#]+)["']""",
            response.text,
            flags=re.IGNORECASE,
        ):

            absolute = urljoin(
                response.url,
                href,
            )


            if (
                "businessanalyst"
                in absolute.lower()
            ):

                urls.add(
                    absolute.split("?")[0]
                )


    return urls


def fetch_mckinsey(source):
    """
    Fetch McKinsey Business Analyst-family roles directly
    from McKinsey's official careers site.

    The generic Workday adapter is deliberately not used.
    """

    search_url = source.get(
        "target",
        (
            "https://www.mckinsey.com/"
            "careers/search-jobs"
        ),
    )


    session = requests.Session()

    session.headers.update(
        HEADERS
    )


    seed_by_url = {
        job["url"]: job
        for job in SEED_JOBS
    }


    candidate_urls = set(
        seed_by_url
    )


    discovered = _discover_urls(
        session,
        search_url,
    )


    candidate_urls.update(
        discovered
    )


    print(
        "  McKinsey candidate URLs: "
        f"{len(candidate_urls)}"
    )


    jobs = []


    for url in sorted(
        candidate_urls
    ):

        seed = seed_by_url.get(
            url,
            {},
        )


        try:

            response = _get(
                session,
                url,
            )

        except Exception as error:

            print(
                "  ⚠️ McKinsey skipped "
                f"{url}: {error}"
            )

            continue


        # ----------------------------------------------------
        # PARSE OFFICIAL JOB PAGE
        # ----------------------------------------------------

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )


        page_text = soup.get_text(
            " ",
            strip=True,
        )


        heading = soup.find(
            "h1"
        )


        title = ""

        if heading:

            title = heading.get_text(
                " ",
                strip=True,
            )


        # Some McKinsey pages are partly client-rendered.
        # Use known metadata as a fallback.

        if (
            not title
            or title.lower()
            in {
                "jobs",
                "search jobs",
            }
        ):

            title = seed.get(
                "title",
                "",
            )


        # ----------------------------------------------------
        # WE ONLY WANT BA-FAMILY RECRUITING
        # ----------------------------------------------------

        if (
            "business analyst"
            not in title.lower()
        ):

            continue


        # ----------------------------------------------------
        # LOCATION
        # ----------------------------------------------------

        location = (
            _target_location(
                page_text
            )
            or seed.get(
                "location",
                "",
            )
        )


        if not location:

            continue


        # ----------------------------------------------------
        # EXCLUDE MEXICO'S 10-12 MONTH IN-SCHOOL PROGRAM
        # ----------------------------------------------------

        if (
            "10-12 month"
            in title.lower()
            or "10–12 month"
            in title.lower()
        ):

            continue


        # ----------------------------------------------------
        # ID
        # ----------------------------------------------------

        job_id = (
            _job_id(url)
            or seed.get(
                "id",
                "",
            )
        )


        if not job_id:

            continue


        jobs.append(
            {

                "global_id": (
                    f"mckinsey:{job_id}"
                ),

                "title": title,

                "location": location,

                "posted_at": "",

                "department": "Consulting",

                "team": "",

                "url": url,

                "apply_url": url,

            }
        )


    # ========================================================
    # DEDUPLICATE
    # ========================================================

    unique = {
        job["global_id"]: job
        for job in jobs
    }


    jobs = list(
        unique.values()
    )


    print(
        "  McKinsey returned: "
        f"{len(jobs)} target roles"
    )


    return jobs
