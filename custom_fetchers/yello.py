import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


REQUEST_TIMEOUT = 30
DETAIL_DELAY = 0.10


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


EARLY_CAREER_TERMS = [
    "intern",
    "internship",
    "graduate",
    "analyst",
    "programme",
    "program",
]


def _clean(text):

    return re.sub(
        r"\s+",
        " ",
        text or "",
    ).strip()


def _target_location(text):

    lower = text.lower()

    locations = []


    if "hong kong" in lower:

        locations.append(
            "Hong Kong"
        )


    if (
        "mexico city" in lower
        or "ciudad de mexico" in lower
        or "ciudad de méxico" in lower
        or "cdmx" in lower
    ):

        locations.append(
            "Mexico City"
        )


    return " | ".join(
        locations
    )


def _is_job_link(url):

    lower = url.lower()

    return (
        "/jobs/" in lower
        or "/external/requisitions/"
        in lower
    )


def _surrounding_text(anchor):

    current = anchor


    for _ in range(5):

        current = current.parent

        if current is None:
            break


        text = _clean(
            current.get_text(
                " ",
                strip=True,
            )
        )


        if (
            "hong kong" in text.lower()
            or "mexico" in text.lower()
        ):

            return text


    return ""


def _detail_location(
    session,
    url,
):

    try:

        response = session.get(
            url,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

    except Exception:

        return ""


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


    return _target_location(
        text
    )


def fetch_yello(source):
    """
    Yello / Recsolu early-career fetcher.

    Used for Deutsche Bank.
    """

    board_url = source[
        "target"
    ]


    session = requests.Session()

    session.headers.update(
        HEADERS
    )


    best_response = None

    best_links = []


    # ========================================================
    # The board is rendered slightly differently depending
    # on locale, so test both.
    # ========================================================

    for locale in [
        "en",
        "de",
    ]:

        try:

            response = session.get(
                board_url,
                params={
                    "locale": locale,
                },
                timeout=REQUEST_TIMEOUT,
            )

            response.raise_for_status()

        except Exception:

            continue


        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )


        links = [

            anchor

            for anchor in soup.find_all(
                "a",
                href=True,
            )

            if _is_job_link(
                urljoin(
                    response.url,
                    anchor["href"],
                )
            )

        ]


        if (
            best_response is None
            or len(links)
            > len(best_links)
        ):

            best_response = response

            best_links = links


    if best_response is None:

        raise RuntimeError(
            "Deutsche Yello board "
            "could not be loaded."
        )


    print(
        "  Yello discovered job links: "
        f"{len(best_links)}"
    )


    jobs_by_url = {}


    for anchor in best_links:

        url = urljoin(
            best_response.url,
            anchor["href"],
        )


        title = _clean(
            anchor.get_text(
                " ",
                strip=True,
            )
        )


        if not title:
            continue


        title_lower = (
            title.lower()
        )


        if not any(
            term in title_lower
            for term in EARLY_CAREER_TERMS
        ):

            continue


        surrounding = (
            _surrounding_text(
                anchor
            )
        )


        location = (
            _target_location(
                surrounding
            )
        )


        if not location:

            location = (
                _detail_location(
                    session,
                    url,
                )
            )


            time.sleep(
                DETAIL_DELAY
            )


        if not location:

            continue


        stable_id = (
            url
            .split("?")[0]
            .rstrip("/")
            .split("/")[-1]
        )


        global_id = (
            "yello:"
            "Deutsche Bank:"
            f"{stable_id}"
        )


        jobs_by_url[
            global_id
        ] = {

            "global_id":
                global_id,

            "title":
                title,

            "location":
                location,

            "posted_at":
                "",

            "department":
                "",

            "team":
                "",

            "url":
                url,

            "apply_url":
                url,
        }


    jobs = list(
        jobs_by_url.values()
    )


    print(
        "  Yello returned: "
        f"{len(jobs)} target-market jobs"
    )


    return jobs
