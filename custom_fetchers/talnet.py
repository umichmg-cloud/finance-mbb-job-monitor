import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


REQUEST_TIMEOUT = 30
PAGE_DELAY = 0.15


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


DETAIL_WORTHY_TERMS = [
    "analyst",
    "intern",
    "internship",
    "graduate",
    "banking",
    "capital markets",
    "advisory",
    "investment",
    "research",
    "wealth",
    "private equity",
    "private capital",
    "credit",
    "markets",
    "m&a",
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


def _job_id(url):
    match = re.search(
        r"/opp/(\d+)-",
        url,
        flags=re.IGNORECASE,
    )

    if match:
        return match.group(1)

    return ""


def _is_opportunity_link(url):
    return bool(
        re.search(
            r"/opp/\d+-",
            url,
            flags=re.IGNORECASE,
        )
    )


def _container_text(anchor):
    """
    TAL.net may render jobs as:
    - table rows
    - list items
    - cards/divs
    """

    container = (
        anchor.find_parent("tr")
        or anchor.find_parent("li")
        or anchor.find_parent("article")
    )


    if container is None:
        container = anchor.parent


    if container is None:
        return ""


    return _clean(
        container.get_text(
            " ",
            strip=True,
        )
    )


def _worth_detail_request(title):
    lower = title.lower()

    return any(
        term in lower
        for term in DETAIL_WORTHY_TERMS
    )


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


def fetch_talnet(source):
    """
    Generic TAL.net / Oleeo-style job board fetcher.

    Currently used for:
    - Bank of America campus
    - Evercore students
    - Rothschild & Co students
    """

    base_url = source[
        "target"
    ]


    company = source[
        "name"
    ]


    page_size = int(
        source.get(
            "page_size",
            50,
        )
    )


    max_pages = int(
        source.get(
            "max_pages",
            10,
        )
    )


    detail_fallback = bool(
        source.get(
            "detail_location_fallback",
            False,
        )
    )


    session = requests.Session()

    session.headers.update(
        HEADERS
    )


    jobs_by_id = {}

    previous_page_ids = set()


    print(
        f"  TAL.net board: {base_url}"
    )


    for page in range(
        max_pages
    ):

        start = (
            page
            * page_size
        )


        try:

            response = session.get(
                base_url,
                params={
                    "start": start,
                },
                timeout=REQUEST_TIMEOUT,
            )

            response.raise_for_status()

        except Exception as error:

            if page == 0:
                raise RuntimeError(
                    f"TAL.net request failed: "
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

            url = urljoin(
                response.url,
                anchor["href"],
            )


            if not _is_opportunity_link(
                url
            ):
                continue


            job_id = _job_id(
                url
            )


            if not job_id:
                continue


            title = _clean(
                anchor.get_text(
                    " ",
                    strip=True,
                )
            )


            if not title:
                continue


            page_ids.add(
                job_id
            )


            global_id = (
                f"talnet:"
                f"{company}:"
                f"{job_id}"
            )


            if global_id in jobs_by_id:
                continue


            surrounding = (
                title
                + " "
                + _container_text(anchor)
            )


            location = (
                _target_location(
                    surrounding
                )
            )


            # Some TAL.net boards don't show location
            # directly on the results card.
            if (
                not location
                and detail_fallback
                and _worth_detail_request(
                    title
                )
            ):

                location = (
                    _detail_location(
                        session,
                        url,
                    )
                )


            # Our monitor only covers HK/CDMX.
            if not location:
                continue


            jobs_by_id[
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


        # ----------------------------------------------------
        # PAGINATION STOP
        # ----------------------------------------------------

        if not page_ids:
            break


        if (
            page > 0
            and page_ids
            == previous_page_ids
        ):
            break


        previous_page_ids = (
            page_ids
        )


        time.sleep(
            PAGE_DELAY
        )


    jobs = list(
        jobs_by_id.values()
    )


    print(
        f"  TAL.net returned: "
        f"{len(jobs)} target-market jobs"
    )


    return jobs
