import re
import time
from urllib.parse import (
    parse_qs,
    urljoin,
    urlparse,
)

import requests
from bs4 import BeautifulSoup


REQUEST_TIMEOUT = 25

PAGE_DELAY = 0.15

PAGE_SIZE = 6


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


# ============================================================
# CURRENT GENERALIST ROLE IDS
#
# Used only as discovery fallbacks.
#
# 10403 is Bain's currently active global Associate
# Consultant Internship.
# ============================================================

FALLBACK_IDS = {
    "10403",
}


def clean(text):

    return re.sub(
        r"\s+",
        " ",
        text or "",
    ).strip()


def extract_job_id(url):

    parsed = urlparse(url)

    query = parse_qs(
        parsed.query
    )


    for key in [
        "folderId",
        "folderid",
        "jobId",
        "jobid",
    ]:

        values = query.get(key)

        if values:

            value = values[0]

            if str(value).isdigit():
                return str(value)


    patterns = [

        r"/JobDetail/[^/]+/(\d+)",

        r"/JobDetail/(\d+)",

        r"/VacancyDetail/(\d+)",

    ]


    for pattern in patterns:

        match = re.search(
            pattern,
            parsed.path,
            flags=re.IGNORECASE,
        )

        if match:
            return match.group(1)


    return ""


def discover_ids(
    session,
    search_url,
    max_pages,
):

    ids = set(
        FALLBACK_IDS
    )


    previous_page_ids = set()


    for page in range(
        max_pages
    ):

        offset = (
            page
            * PAGE_SIZE
        )


        try:

            response = session.get(
                search_url,
                params={
                    "jobOffset": offset,
                },
                timeout=REQUEST_TIMEOUT,
            )

            response.raise_for_status()

        except Exception as error:

            print(
                "  ⚠️ Bain search page failed: "
                f"{error}"
            )

            break


        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )


        page_ids = set()


        for anchor in soup.find_all(
            "a",
            href=True,
        ):

            absolute = urljoin(
                response.url,
                anchor["href"],
            )


            job_id = extract_job_id(
                absolute
            )


            if job_id:

                page_ids.add(job_id)

                ids.add(job_id)


        # ----------------------------------------------------
        # STOP IF PAGINATION IS REPEATING
        # ----------------------------------------------------

        if (
            page > 0
            and page_ids
            == previous_page_ids
        ):
            break


        if not page_ids:
            break


        previous_page_ids = (
            page_ids
        )


        time.sleep(
            PAGE_DELAY
        )


    return ids


def parse_bain_job(
    session,
    job_id,
):

    url = (
        "https://www.bain.com/"
        "careers/find-a-role/"
        "position/"
        f"?jobid={job_id}"
    )


    try:

        response = session.get(
            url,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

    except Exception:

        return None


    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )


    text = soup.get_text(
        "\n",
        strip=True,
    )


    # --------------------------------------------------------
    # CLOSED JOB
    # --------------------------------------------------------

    if (
        "job not available"
        in text.lower()
    ):

        return None


    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    title = ""


    for heading in soup.find_all(
        ["h1", "h2"]
    ):

        candidate = clean(
            heading.get_text(
                " ",
                strip=True,
            )
        )


        lower = candidate.lower()


        if (
            "associate consultant"
            in lower
        ):

            title = candidate

            break


    if not title:

        return None


    # --------------------------------------------------------
    # ONLY GENERALIST AC / ACI
    # --------------------------------------------------------

    title_lower = title.lower()


    if (
        "associate consultant"
        not in title_lower
    ):

        return None


    if (
        "senior associate consultant"
        in title_lower
    ):

        return None


    # --------------------------------------------------------
    # LOCATION SECTION
    #
    # IMPORTANT:
    # We CANNOT search the whole page for "Hong Kong".
    #
    # Bain's global navigation always lists every office.
    #
    # We only inspect the actual Location(s) section.
    # --------------------------------------------------------

    lower_text = text.lower()


    marker = lower_text.find(
        "location(s)"
    )


    if marker == -1:

        return None


    location_text = text[
        marker:
        marker + 2500
    ]


    lower_location = (
        location_text.lower()
    )


    locations = []


    if "hong kong" in lower_location:

        locations.append(
            "Hong Kong"
        )


    if "mexico city" in lower_location:

        locations.append(
            "Mexico City"
        )


    if not locations:

        return None


    return {

        "global_id":
            f"bain:{job_id}",

        "title":
            title,

        "location":
            " | ".join(
                locations
            ),

        "posted_at":
            "",

        "department":
            "Management Consulting",

        "team":
            "General Consulting",

        "url":
            url,

        "apply_url":
            url,

    }


def fetch_bain(source):

    session = requests.Session()

    session.headers.update(
        HEADERS
    )


    search_url = source[
        "target"
    ]


    max_pages = int(
        source.get(
            "max_pages",
            120,
        )
    )


    ids = discover_ids(
        session,
        search_url,
        max_pages,
    )


    print(
        "  Bain discovered IDs: "
        f"{len(ids)}"
    )


    jobs = []


    for job_id in sorted(ids):

        job = parse_bain_job(
            session,
            job_id,
        )


        if job:

            jobs.append(job)


    print(
        "  Bain returned: "
        f"{len(jobs)} target roles"
    )


    return jobs
