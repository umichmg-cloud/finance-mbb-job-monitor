import re
import time

import requests
from bs4 import BeautifulSoup


REQUEST_TIMEOUT = 30
MAX_RETRIES = 3


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
    "Accept-Language":
        "en-US,en;q=0.9",
}


KNOWN_GENERALIST_IDS = {
    "10403",
}


def _clean(text):

    return re.sub(
        r"\s+",
        " ",
        text or "",
    ).strip()


def _get(session, url):

    last_error = None


    for attempt in range(
        1,
        MAX_RETRIES + 1,
    ):

        try:

            response = session.get(
                url,
                timeout=REQUEST_TIMEOUT,
            )

            response.raise_for_status()

            return response

        except Exception as error:

            last_error = error


            if attempt < MAX_RETRIES:

                time.sleep(
                    attempt
                )


    raise RuntimeError(
        str(last_error)
    )


def _parse_job(
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

        response = _get(
            session,
            url,
        )

    except Exception as error:

        print(
            f"  ⚠️ Bain {job_id} "
            f"request failed: {error}"
        )

        return None


    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )


    text = _clean(
        soup.get_text(
            " ",
            strip=True,
        )
    )


    lower = text.lower()


    if "job not available" in lower:

        print(
            f"  Bain {job_id}: closed"
        )

        return None


    # ========================================================
    # TITLE
    # ========================================================

    title = ""


    if (
        "associate consultant internship"
        in lower
    ):

        title = (
            "Associate Consultant Internship"
        )

    elif (
        "associate consultant intern"
        in lower
    ):

        title = (
            "Associate Consultant Intern"
        )

    elif (
        "associate consultant"
        in lower
    ):

        title = (
            "Associate Consultant"
        )


    if not title:

        print(
            f"  Bain {job_id}: "
            "generalist title not found"
        )

        return None


    # ========================================================
    # LOCATION(S)
    # ========================================================

    marker = lower.find(
        "location(s)"
    )


    if marker == -1:

        print(
            f"  Bain {job_id}: "
            "Location(s) section not found"
        )

        return None


    location_section = (
        text[
            marker:
            marker + 6000
        ]
        .lower()
    )


    locations = []


    if (
        "hong kong"
        in location_section
    ):

        locations.append(
            "Hong Kong"
        )


    if (
        "mexico city"
        in location_section
    ):

        locations.append(
            "Mexico City"
        )


    if not locations:

        print(
            f"  Bain {job_id}: "
            "not HK/CDMX"
        )

        return None


    print(
        f"  Bain {job_id}: "
        f"{title} | "
        f"{' | '.join(locations)}"
    )


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


    jobs = []


    for job_id in sorted(
        KNOWN_GENERALIST_IDS
    ):

        job = _parse_job(
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
