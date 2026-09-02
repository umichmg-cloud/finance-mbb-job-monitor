import re
import time
from urllib.parse import (
    parse_qs,
    urlencode,
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
            "Hong Kong SAR"
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
    parsed = urlparse(
        url
    )

    query = parse_qs(
        parsed.query
    )


    for key in [
        "jobid",
        "jobId",
        "JobId",
    ]:

        values = query.get(
            key
        )

        if values:
            return str(
                values[0]
            )


    match = re.search(
        r"jobid[=:](\d+)",
        url,
        flags=re.IGNORECASE,
    )


    if match:
        return match.group(1)


    return ""


def _title(anchor):
    title = _clean(
        anchor.get_text(
            " ",
            strip=True,
        )
    )


    if (
        title
        and len(title) > 4
        and title.lower()
        not in {
            "apply",
            "share",
            "show more",
        }
    ):
        return title


    parent = (
        anchor.find_parent("li")
        or anchor.find_parent("article")
        or anchor.find_parent("div")
    )


    if parent:

        heading = parent.find(
            [
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


def _job_url(
    target,
    partner_id,
    site_id,
    job_id,
):
    query = urlencode(
        {
            "PageType":
                "JobDetails",
            "jobid":
                job_id,
            "partnerid":
                partner_id,
            "siteid":
                site_id,
        }
    )


    base = (
        target
        .split("?")[0]
    )


    return (
        base
        + "?"
        + query
    )


def fetch_brassring(source):
    """
    BrassRing / TGnewUI fetcher.

    Currently used for UBS Graduate Board.
    """

    target = source[
        "target"
    ]


    company = source[
        "name"
    ]


    partner_id = str(
        source["partner_id"]
    )


    site_id = str(
        source["site_id"]
    )


    max_pages = int(
        source.get(
            "max_pages",
            20,
        )
    )


    page_step = int(
        source.get(
            "page_step",
            10,
        )
    )


    session = requests.Session()

    session.headers.update(
        HEADERS
    )


    jobs_by_id = {}

    previous_page_ids = set()


    print(
        "  BrassRing board: "
        f"partner={partner_id}, "
        f"site={site_id}"
    )


    for page in range(
        max_pages
    ):

        record_start = (
            1
            + page
            * page_step
        )


        params = {
            "PageType":
                "searchResults",
            "SearchType":
                "linkquery",
            "partnerid":
                partner_id,
            "siteid":
                site_id,
            "recordstart":
                record_start,
        }


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
                    f"BrassRing request failed: "
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


            job_id = _job_id(
                absolute
            )


            if not job_id:
                continue


            title = _title(
                anchor
            )


            if not title:
                continue


            parent = (
                anchor.find_parent("li")
                or anchor.find_parent(
                    "article"
                )
                or anchor.find_parent(
                    "div"
                )
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


            page_ids.add(
                job_id
            )


            if not location:
                continue


            global_id = (
                f"brassring:"
                f"{company}:"
                f"{job_id}"
            )


            url = _job_url(
                target,
                partner_id,
                site_id,
                job_id,
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


        # ----------------------------------------------------
        # STOP REPEATING PAGE
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
        f"  BrassRing returned: "
        f"{len(jobs)} target-market jobs"
    )


    return jobs
