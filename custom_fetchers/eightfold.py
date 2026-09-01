import time
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests


PAGE_SIZE = 10
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
PAGE_DELAY = 0.15


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/131.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
}


def _first_value(data, keys):
    for key in keys:
        value = data.get(key)

        if value not in (None, "", []):
            return value

    return None


def _location_value(value):
    if not value:
        return ""

    if isinstance(value, str):
        return value.strip()

    if isinstance(value, dict):

        direct = _first_value(
            value,
            [
                "name",
                "displayName",
                "display_name",
            ],
        )

        if direct:
            return str(direct).strip()

        parts = []

        for key in [
            "city",
            "state",
            "region",
            "country",
        ]:
            item = value.get(key)

            if item:
                parts.append(
                    str(item).strip()
                )

        return ", ".join(parts)

    return str(value).strip()


def _get_location(position):
    locations = []

    for key in [
        "primaryLocation",
        "primary_location",
        "location",
    ]:

        value = _location_value(
            position.get(key)
        )

        if value:
            locations.append(value)


    multiple = position.get("locations")

    if isinstance(multiple, list):

        for item in multiple:

            value = _location_value(item)

            if value:
                locations.append(value)


    unique = []

    for location in locations:

        if location not in unique:
            unique.append(location)


    return " | ".join(unique)


def _get_title(position):
    value = _first_value(
        position,
        [
            "name",
            "title",
            "postingName",
            "posting_name",
            "positionName",
            "position_name",
        ],
    )

    if value:
        return str(value).strip()

    return ""


def _get_id(position):
    value = _first_value(
        position,
        [
            "id",
            "positionId",
            "position_id",
            "jobId",
            "job_id",
            "displayJobId",
            "display_job_id",
            "reqId",
            "requisitionId",
            "requisition_id",
        ],
    )

    if value is None:
        return ""

    return str(value).strip()


def _get_posted_at(position):
    value = _first_value(
        position,
        [
            "postedTs",
            "creationTs",
            "t_create",
            "t_update",
            "posted_at",
            "postedAt",
        ],
    )

    if value in (None, ""):
        return ""

    try:
        number = float(value)

        if number > 10_000_000_000:
            number /= 1000

        dt = datetime.fromtimestamp(
            number,
            tz=timezone.utc,
        )

        return dt.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    except (
        TypeError,
        ValueError,
        OSError,
    ):
        return str(value).strip()


def _get_url(
    position,
    base_url,
    job_id,
):
    value = _first_value(
        position,
        [
            "canonicalPositionUrl",
            "canonical_position_url",
            "applyUrl",
            "apply_url",
            "jobUrl",
            "job_url",
            "url",
        ],
    )

    if value:

        value = str(value).strip()

        if value.startswith("http"):
            return value

        return urljoin(
            base_url + "/",
            value,
        )


    if job_id:

        return (
            base_url.rstrip("/")
            + "/careers?pid="
            + job_id
        )


    return ""


def _extract_positions(data):
    """
    Eightfold currently exposes two common response formats:

    Classic:
        {
            "positions": [...],
            "count": ...
        }

    PCS-X:
        {
            "data": {
                "positions": [...],
                "count": ...
            }
        }
    """

    if not isinstance(data, dict):
        return [], None


    nested = data.get("data")

    if isinstance(nested, dict):

        positions = nested.get(
            "positions",
            [],
        )

        count = nested.get("count")

    else:

        positions = data.get(
            "positions",
            [],
        )

        count = data.get("count")


    if not isinstance(positions, list):
        positions = []


    return positions, count


def _request(
    session,
    url,
    params,
):
    last_error = None

    for attempt in range(
        1,
        MAX_RETRIES + 1,
    ):

        try:

            response = session.get(
                url,
                params=params,
                timeout=REQUEST_TIMEOUT,
            )

            response.raise_for_status()

            return response.json()

        except Exception as error:

            last_error = error

            if attempt < MAX_RETRIES:

                time.sleep(
                    attempt * 1.5
                )


    raise RuntimeError(
        f"Eightfold request failed: "
        f"{last_error}"
    )


def _probe_endpoint(
    session,
    url,
    domain,
):
    params = {
        "domain": domain,
        "start": 0,
        "num": PAGE_SIZE,
    }

    try:

        data = _request(
            session,
            url,
            params,
        )

        positions, count = (
            _extract_positions(data)
        )

        if positions:

            return True, positions, count

        return False, positions, count

    except Exception:

        return False, [], None


def fetch_eightfold(source):
    """
    Generic Eightfold fetcher.

    It tries both currently common public Eightfold
    search APIs:

        /api/pcsx/search
        /api/apply/v2/jobs

    This allows the same fetcher to support BCG,
    HSBC and future Eightfold employers.
    """

    base_url = (
        source["target"]
        .rstrip("/")
    )

    domain = source.get(
        "domain",
        "",
    )

    max_pages = int(
        source.get(
            "max_pages",
            200,
        )
    )


    session = requests.Session()

    session.headers.update(
        HEADERS
    )


    candidate_endpoints = [
        (
            base_url
            + "/api/pcsx/search"
        ),
        (
            base_url
            + "/api/apply/v2/jobs"
        ),
    ]


    selected_endpoint = None


    print(
        f"  Eightfold host: "
        f"{base_url}"
    )


    for endpoint in candidate_endpoints:

        working, positions, count = (
            _probe_endpoint(
                session,
                endpoint,
                domain,
            )
        )

        if working:

            selected_endpoint = endpoint

            print(
                "  Eightfold endpoint: "
                f"{endpoint}"
            )

            break


    if not selected_endpoint:

        raise RuntimeError(
            "No public Eightfold jobs endpoint "
            "returned positions."
        )


    jobs_by_id = {}


    for page in range(max_pages):

        start = (
            page * PAGE_SIZE
        )

        params = {
            "domain": domain,
            "start": start,
            "num": PAGE_SIZE,
        }


        data = _request(
            session,
            selected_endpoint,
            params,
        )


        positions, count = (
            _extract_positions(data)
        )


        if not positions:
            break


        for position in positions:

            if not isinstance(
                position,
                dict,
            ):
                continue


            title = _get_title(
                position
            )

            if not title:
                continue


            job_id = _get_id(
                position
            )


            url = _get_url(
                position,
                base_url,
                job_id,
            )


            if job_id:

                global_id = (
                    "eightfold:"
                    + source["name"]
                    + ":"
                    + job_id
                )

            elif url:

                global_id = (
                    "eightfold:"
                    + source["name"]
                    + ":"
                    + url
                )

            else:

                continue


            department = _first_value(
                position,
                [
                    "department",
                    "category",
                    "jobCategory",
                    "job_category",
                    "businessUnit",
                    "business_unit",
                ],
            )


            jobs_by_id[global_id] = {
                "global_id": global_id,
                "title": title,
                "location": _get_location(
                    position
                ),
                "posted_at": _get_posted_at(
                    position
                ),
                "department": (
                    str(department).strip()
                    if department
                    else ""
                ),
                "team": "",
                "url": url,
                "apply_url": url,
            }


        if len(positions) < PAGE_SIZE:
            break


        time.sleep(
            PAGE_DELAY
        )


    jobs = list(
        jobs_by_id.values()
    )


    print(
        f"  Eightfold returned: "
        f"{len(jobs)} unique jobs"
    )


    return jobs
