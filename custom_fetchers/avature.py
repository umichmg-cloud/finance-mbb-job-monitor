import re
import time

from urllib.parse import (
    parse_qs,
    urljoin,
    urlparse,
)

import requests
from bs4 import BeautifulSoup


PAGE_SIZE = 6

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


def _get(
    session,
    url,
    params=None,
):

    response = session.get(
        url,
        params=params,
        timeout=REQUEST_TIMEOUT,
        allow_redirects=True,
    )

    response.raise_for_status()

    return response


def _clean(text):

    return re.sub(
        r"\s+",
        " ",
        text or "",
    ).strip()


def _job_id(url):

    parsed = urlparse(
        url
    )


    query = parse_qs(
        parsed.query
    )


    for key in [
        "folderId",
        "folderid",
        "jobId",
        "jobid",
    ]:

        value = query.get(
            key
        )

        if value:

            return str(
                value[0]
            )


    match = re.search(
        r"/JobDetail/[^/]+/(\d+)",
        parsed.path,
        flags=re.IGNORECASE,
    )


    if match:

        return match.group(1)


    return url


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
    ):

        locations.append(
            "Mexico City"
        )


    return " | ".join(
        locations
    )


def _posted_date(text):

    match = re.search(
        r"Posted\s+"
        r"(\d{1,2})-"
        r"([A-Za-z]{3})-"
        r"(\d{4})",
        text,
        flags=re.IGNORECASE,
    )


    if not match:

        return ""


    months = {

        "jan": "01",
        "feb": "02",
        "mar": "03",
        "apr": "04",
        "may": "05",
        "jun": "06",
        "jul": "07",
        "aug": "08",
        "sep": "09",
        "oct": "10",
        "nov": "11",
        "dec": "12",

    }


    month = months.get(
        match.group(2).lower()
    )


    if not month:

        return ""


    return (
        f"{match.group(3)}-"
        f"{month}-"
        f"{int(match.group(1)):02d} "
        "00:00:00"
    )


def _is_job_link(anchor):

    href = anchor.get(
        "href",
        "",
    ).lower()


    return (
        "/jobdetail/" in href
        or "folderdetail" in href
    )


def _parse_page(
    html,
    base_url,
):

    soup = BeautifulSoup(
        html,
        "html.parser",
    )


    jobs = []

    seen = set()


    # ========================================================
    # STANDARD AVATURE RESULT CARDS
    # ========================================================

    for article in soup.find_all(
        "article"
    ):

        classes = " ".join(
            article.get(
                "class",
                [],
            )
        ).lower()


        if (
            "article--result"
            not in classes
        ):

            continue


        anchor = None


        for candidate in article.find_all(
            "a",
            href=True,
        ):

            if _is_job_link(
                candidate
            ):

                anchor = candidate

                break


        if not anchor:

            continue


        title = _clean(
            anchor.get_text(
                " ",
                strip=True,
            )
        )


        if not title:

            heading = article.find(
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


        url = urljoin(
            base_url,
            anchor["href"],
        )


        text = _clean(
            article.get_text(
                " ",
                strip=True,
            )
        )


        jobs.append(
            {

                "id": _job_id(
                    url
                ),

                "title": title,

                "url": url,

                "location": (
                    _target_location(
                        text
                    )
                ),

                "posted_at": (
                    _posted_date(
                        text
                    )
                ),

            }
        )


        seen.add(
            url
        )


    # ========================================================
    # FALLBACK FOR BAIN'S BRANDED AVATURE PAGES
    # ========================================================

    for anchor in soup.find_all(
        "a",
        href=True,
    ):

        if not _is_job_link(
            anchor
        ):

            continue


        url = urljoin(
            base_url,
            anchor["href"],
        )


        if url in seen:

            continue


        title = _clean(
            anchor.get_text(
                " ",
                strip=True,
            )
        )


        parent = (
            anchor.find_parent(
                "article"
            )
            or anchor.find_parent(
                "li"
            )
            or anchor.find_parent(
                "div"
            )
        )


        if (
            not title
            or len(title) < 3
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


        surrounding = ""


        if parent:

            surrounding = _clean(
                parent.get_text(
                    " ",
                    strip=True,
                )
            )


        jobs.append(
            {

                "id": _job_id(
                    url
                ),

                "title": title,

                "url": url,

                "location": (
                    _target_location(
                        surrounding
                    )
                ),

                "posted_at": (
                    _posted_date(
                        surrounding
                    )
                ),

            }
        )


        seen.add(
            url
        )


    return jobs


def _possible_search_urls(
    source,
):

    branded = source[
        "target"
    ].rstrip("/")


    native = source.get(
        "avature_origin",
        "https://bain.avature.net",
    ).rstrip("/")


    candidates = [

        (
            branded
            + "/careers/SearchJobs"
        ),

        (
            branded
            + "/jobs/SearchJobs"
        ),

        (
            native
            + "/careers/SearchJobs"
        ),

        (
            native
            + "/jobs/SearchJobs"
        ),

    ]


    unique = []


    for url in candidates:

        if url not in unique:

            unique.append(
                url
            )


    return unique


def _find_search_url(
    session,
    source,
):

    for url in _possible_search_urls(
        source
    ):

        try:

            response = _get(
                session,
                url,
                params={
                    "jobOffset": 0,
                },
            )

        except Exception:

            continue


        jobs = _parse_page(
            response.text,
            response.url,
        )


        if jobs:

            final_url = (
                response.url
                .split("?")[0]
            )


            print(
                "  Bain Avature search: "
                f"{final_url}"
            )


            return (
                final_url,
                jobs,
            )


    raise RuntimeError(
        "No Bain Avature SearchJobs "
        "endpoint returned results."
    )


def _detail_target_location(
    session,
    url,
):

    try:

        response = _get(
            session,
            url,
        )

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


def fetch_avature(source):
    """
    Avature fetcher currently used for Bain.

    We specifically care about Bain's undergraduate
    Associate Consultant family of positions.
    """

    max_pages = int(
        source.get(
            "max_pages",
            120,
        )
    )


    role_terms = [

        term.lower()

        for term in source.get(
            "role_terms",
            [
                "associate consultant",
            ],
        )

    ]


    session = requests.Session()

    session.headers.update(
        HEADERS
    )


    search_url, first_page = (
        _find_search_url(
            session,
            source,
        )
    )


    jobs_by_id = {}


    offset_parameter = (
        "jobOffset"
    )


    previous_ids = set()


    # ========================================================
    # PAGINATION
    # ========================================================

    for page in range(
        max_pages
    ):


        if page == 0:

            page_jobs = (
                first_page
            )


        else:

            offset = (
                page
                * PAGE_SIZE
            )


            response = _get(
                session,
                search_url,
                params={
                    offset_parameter:
                    offset,
                },
            )


            page_jobs = _parse_page(
                response.text,
                response.url,
            )


            current_ids = {

                str(job["id"])

                for job in page_jobs

            }


            # =================================================
            # AVATURE FALLBACK:
            #
            # Some branded tenants ignore jobOffset and use
            # "offset" instead.
            # =================================================

            if (
                page == 1
                and (
                    not page_jobs
                    or current_ids
                    == previous_ids
                )
            ):

                response = _get(
                    session,
                    search_url,
                    params={
                        "offset":
                        offset,
                    },
                )


                alternate = _parse_page(
                    response.text,
                    response.url,
                )


                alternate_ids = {

                    str(job["id"])

                    for job in alternate

                }


                if (
                    alternate
                    and alternate_ids
                    != previous_ids
                ):

                    offset_parameter = (
                        "offset"
                    )

                    page_jobs = (
                        alternate
                    )


        if not page_jobs:

            break


        page_ids = {

            str(job["id"])

            for job in page_jobs

        }


        # ====================================================
        # PROCESS RESULTS
        # ====================================================

        for job in page_jobs:


            title_lower = (
                job["title"]
                .lower()
            )


            # Bain undergraduate recruiting:
            # Associate Consultant / Associate Consultant Intern

            if not any(
                term
                in title_lower
                for term
                in role_terms
            ):

                continue


            # ------------------------------------------------
            # GET TARGET LOCATION FROM DETAIL PAGE
            # ------------------------------------------------

            detail_location = (
                _detail_target_location(
                    session,
                    job["url"],
                )
            )


            location = (
                detail_location
                or job["location"]
            )


            # No HK/Mexico location found.
            if not location:

                continue


            job_id = str(
                job["id"]
            )


            global_id = (
                f"bain:{job_id}"
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
                    job["posted_at"],

                "department":
                    "Consulting",

                "team":
                    "",

                "url":
                    job["url"],

                "apply_url":
                    job["url"],

            }


        # ====================================================
        # STOP CONDITIONS
        # ====================================================

        if (
            page > 0
            and page_ids
            == previous_ids
        ):

            break


        previous_ids = (
            page_ids
        )


        if (
            len(page_jobs)
            < PAGE_SIZE
        ):

            break


        time.sleep(
            PAGE_DELAY
        )


    jobs = list(
        jobs_by_id.values()
    )


    print(
        "  Bain Avature returned: "
        f"{len(jobs)} target-market jobs"
    )


    return jobs
