import re
from urllib.parse import urljoin, urlparse

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


def _job_id(url):
    path = (
        urlparse(url)
        .path
        .rstrip("/")
    )


    value = (
        path
        .split("/")[-1]
    )


    if value:
        return value


    return url


def _container(anchor):
    return (
        anchor.find_parent("article")
        or anchor.find_parent("li")
        or anchor.find_parent("div")
    )


def _title(anchor):
    text = _clean(
        anchor.get_text(
            " ",
            strip=True,
        )
    )


    if (
        text
        and text.lower()
        not in {
            "apply",
            "view",
            "learn more",
        }
    ):
        return text


    parent = _container(
        anchor
    )


    if parent:

        heading = parent.find(
            [
                "h1",
                "h2",
                "h3",
                "h4",
            ]
        )

        if heading:

            return _clean(
                heading.get_text(
                    " ",
                    strip=True,
                )
            )


    return ""


def fetch_yello(source):
    """
    Yello / Recsolu fetcher.

    Currently used for Deutsche Bank early careers.
    """

    board_url = source[
        "target"
    ]


    company = source[
        "name"
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


    jobs_by_id = {}


    print(
        f"  Yello board: "
        f"{board_url}"
    )


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


        title = _title(
            anchor
        )


        if not title:
            continue


        parent = _container(
            anchor
        )


        surrounding = title


        if parent:

            surrounding += (
                " "
                + _clean(
                    parent.get_text(
                        " ",
                        strip=True,
                    )
                )
            )


        location = (
            _target_location(
                surrounding
            )
        )


        if not location:
            continue


        job_id = _job_id(
            url
        )


        global_id = (
            f"yello:"
            f"{company}:"
            f"{job_id}"
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
        f"  Yello returned: "
        f"{len(jobs)} target-market jobs"
    )


    return jobs
