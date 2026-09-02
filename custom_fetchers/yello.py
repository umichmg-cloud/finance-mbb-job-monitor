import re
from urllib.parse import urljoin

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
    "Accept-Language":
        "en-US,en;q=0.9",
}


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


def _card_text(anchor):
    """
    Walk upward until we find the Yello result card
    containing title + country + city.
    """

    node = anchor


    for _ in range(6):

        node = node.parent

        if node is None:
            break


        text = _clean(
            node.get_text(
                " ",
                strip=True,
            )
        )


        lower = text.lower()


        if (
            "hong kong"
            in lower
            or "mexico city"
            in lower
            or "ciudad de mexico"
            in lower
        ):

            return text


    return ""


def fetch_yello(source):

    board_url = source[
        "target"
    ]


    session = requests.Session()

    session.headers.update(
        HEADERS
    )


    response = session.get(
        board_url,
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()


    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )


    all_job_links = []



    for anchor in soup.find_all(
        "a",
        href=True,
    ):

        url = urljoin(
            response.url,
            anchor["href"],
        )


        if not _is_job_link(
            url
        ):
            continue


        all_job_links.append(
            (
                anchor,
                url,
            )
        )


    print(
        "  Yello discovered job links: "
        f"{len(all_job_links)}"
    )


    jobs_by_id = {}


    for anchor, url in (
        all_job_links
    ):

        title = _clean(
            anchor.get_text(
                " ",
                strip=True,
            )
        )


        if not title:
            continue


        surrounding = (
            _card_text(
                anchor
            )
        )


        location = (
            _target_location(
                surrounding
            )
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


    jobs = list(
        jobs_by_id.values()
    )


    print(
        "  Yello target-market jobs: "
        f"{len(jobs)}"
    )


    return jobs
