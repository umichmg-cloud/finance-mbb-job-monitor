import re
import time
from urllib.parse import (
    parse_qs,
    urljoin,
    urlparse,
)

import requests
from bs4 import BeautifulSoup


REQUEST_TIMEOUT = 30
PAGE_DELAY = 0.20


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Macintosh; Intel Mac OS X 10_15_7) "
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
    "Cache-Control":
        "no-cache",
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
        "/jobdetail/" in lower
        or "/vacancydetail/" in lower
    )


def _job_id(url):
    parsed = urlparse(
        url
    )


    query = parse_qs(
        parsed.query
    )


    for key in [
        "jobId",
        "jobid",
        "folderId",
        "folderid",
    ]:

        values = query.get(
            key
        )

        if values:
            return str(
                values[0]
            )


    match = re.search(
        r"/(?:JobDetail|VacancyDetail)/"
        r".*?/(\d+)(?:/|$)",
        parsed.path,
        flags=re.IGNORECASE,
    )


    if match:
        return match.group(1)


    # Stable fallback from complete path.
    return (
        parsed.path
        .rstrip("/")
        .replace("/", ":")
    )


def _parse_results(
    html,
    base_url,
):
    soup = BeautifulSoup(
        html,
        "html.parser",
    )


    results = []

    seen = set()


    for anchor in soup.find_all(
        "a",
        href=True,
    ):

        url = urljoin(
            base_url,
            anchor["href"],
        )


        if not _is_job_link(
            url
        ):
            continue


        if url in seen:
            continue


        seen.add(url)


        title = _clean(
            anchor.get_text(
                " ",
                strip=True,
            )
        )


        parent = (
            anchor.find_parent("article")
            or anchor.find_parent("li")
            or anchor.find_parent("div")
        )


        if (
            not title
            or len(title) < 4
        ):

            if parent:

                heading = parent.find(
                    [
                        "h2",
                        "h3",
                        "h4",
                    ]
                )

                if heading:

                    title = _clean(
                        heading.get_text(
                            " ",
                            strip=True,
                        )
                    )


        if not title:
            continue


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


        results.append(
            {
                "id":
                    _job_id(url),

                "title":
                    title,

                "location":
                    _target_location(
                        surrounding
                    ),

                "url":
                    url,
            }
        )


    return results


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


    return _target_location(
        soup.get_text(
            " ",
            strip=True,
        )
    )


def fetch_avature(source):
    """
    Generic Avature SearchJobs fetcher.

    Currently used for Macquarie Graduate / Intern roles.
    """

    target = source[
        "target"
    ]


    company = source[
        "name"
    ]


    records_per_page = int(
        source.get(
            "records_per_page",
            50,
        )
    )


    max_pages = int(
        source.get(
            "max_pages",
            10,
        )
    )


    search_params = dict(
        source.get(
            "search_params",
            {},
        )
    )


    session = requests.Session()

    session.headers.update(
        HEADERS
    )


    jobs_by_id = {}

    previous_ids = set()


    print(
        f"  Avature board: "
        f"{target}"
    )


    for page in range(
        max_pages
    ):

        params = dict(
            search_params
        )


        params[
            "jobRecordsPerPage"
        ] = records_per_page


        params[
            "jobOffset"
        ] = (
            page
            * records_per_page
        )


        try:

            response = session.get(
                target,
                params=params,
                timeout=REQUEST_TIMEOUT,
            )

            response.raise_for_status()

        except Exception as error:

            if page == 0:
                raise RuntimeError(
                    f"Avature request failed: "
                    f"{error}"
                )

            break


        results = _parse_results(
            response.text,
            response.url,
        )


        if not results:
            break


        page_ids = {
            str(job["id"])
            for job in results
        }


        if (
            page > 0
            and page_ids
            == previous_ids
        ):
            break


        previous_ids = (
            page_ids
        )


        for job in results:

            location = job[
                "location"
            ]


            if not location:

                location = (
                    _detail_location(
                        session,
                        job["url"],
                    )
                )


            if not location:
                continue


            global_id = (
                f"avature:"
                f"{company}:"
                f"{job['id']}"
            )


            jobs_by_id[
                global_id
            ] = {

                "global_id":
                    global_id,

                "title":
                    job["title"],

                "location":
                    location,

                "posted_at":
                    "",

                "department":
                    "",

                "team":
                    "",

                "url":
                    job["url"],

                "apply_url":
                    job["url"],
            }


        time.sleep(
            PAGE_DELAY
        )


    jobs = list(
        jobs_by_id.values()
    )


    print(
        f"  Avature returned: "
        f"{len(jobs)} target-market jobs"
    )


    return jobs
