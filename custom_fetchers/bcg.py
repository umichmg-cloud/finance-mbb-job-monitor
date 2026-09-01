import time
from datetime import datetime, timezone

import requests


# ============================================================
# SETTINGS
# ============================================================

PAGE_SIZE = 10

PAGE_PAUSE_SECONDS = 0.20

REQUEST_TIMEOUT_SECONDS = 30

MAX_RETRIES = 3


BROWSER_HEADERS = {
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


# ============================================================
# HELPERS
# ============================================================

def timestamp_to_string(value):
    """
    Eightfold commonly returns timestamps as Unix seconds.

    Convert them into the format used by our monitor.
    """

    if value in (None, ""):
        return ""

    try:

        value = float(value)

        # Some APIs return milliseconds rather than seconds.
        if value > 10_000_000_000:
            value = value / 1000

        dt = datetime.fromtimestamp(
            value,
            tz=timezone.utc,
        )

        return dt.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    except (TypeError, ValueError, OSError):
        return str(value)


def location_to_string(location):
    """
    Convert either a string or a structured Eightfold
    location object into readable text.
    """

    if not location:
        return ""

    if isinstance(location, str):
        return location.strip()

    if isinstance(location, dict):

        # Some tenants give us a ready-made name.
        for key in [
            "name",
            "displayName",
            "display_name",
        ]:

            value = location.get(key)

            if value:
                return str(value).strip()


        parts = []

        for key in [
            "city",
            "state",
            "country",
        ]:

            value = location.get(key)

            if value:
                parts.append(
                    str(value).strip()
                )

        return ", ".join(parts)


    return str(location).strip()


def assemble_location(position):
    """
    Eightfold can return:

    location
    locations[]
    primaryLocation
    primary_location

    We combine all available locations.

    This is especially important for consulting roles
    which can be open in several offices.
    """

    locations = []


    # --------------------------------------------------------
    # FLAT LOCATION
    # --------------------------------------------------------

    flat_location = (
        position.get("location")
        or position.get("primaryLocation")
        or position.get("primary_location")
    )

    flat_location = location_to_string(
        flat_location
    )

    if flat_location:
        locations.append(flat_location)


    # --------------------------------------------------------
    # MULTIPLE LOCATIONS
    # --------------------------------------------------------

    multiple = position.get("locations")

    if isinstance(multiple, list):

        for item in multiple:

            text = location_to_string(item)

            if text:
                locations.append(text)


    # --------------------------------------------------------
    # REMOVE DUPLICATES
    # --------------------------------------------------------

    unique_locations = []

    for location in locations:

        if location not in unique_locations:
            unique_locations.append(location)


    return " | ".join(
        unique_locations
    )


def get_title(position):
    """
    Eightfold tenants use slightly different title fields.
    """

    for key in [
        "name",
        "posting_name",
        "postingName",
        "title",
    ]:

        value = position.get(key)

        if value:
            return str(value).strip()

    return ""


def get_job_id(position):
    """
    Obtain the most stable ID available.
    """

    for key in [
        "id",
        "display_job_id",
        "displayJobId",
        "job_id",
        "jobId",
        "reqId",
    ]:

        value = position.get(key)

        if value not in (None, ""):
            return str(value).strip()

    return ""


def get_job_url(position, job_id):
    """
    Prefer Eightfold's canonical job URL.
    """

    for key in [
        "canonicalPositionUrl",
        "canonical_position_url",
        "applyUrl",
        "apply_url",
        "jobUrl",
        "job_url",
    ]:

        value = position.get(key)

        if value:
            return str(value).strip()


    # Fallback URL.

    if job_id:

        return (
            "https://careers.bcg.com/"
            f"careers?pid={job_id}"
        )


    return ""


def request_page(
    session,
    api_url,
    domain,
    start,
):
    """
    Request one page from BCG's public Eightfold endpoint.
    """

    params = {
        "domain": domain,
        "start": start,
        "num": PAGE_SIZE,
    }


    last_error = None


    for attempt in range(
        1,
        MAX_RETRIES + 1,
    ):

        try:

            response = session.get(
                api_url,
                params=params,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )

            response.raise_for_status()

            data = response.json()

            if not isinstance(data, dict):

                raise ValueError(
                    "BCG returned non-dictionary JSON"
                )

            return data


        except Exception as error:

            last_error = error

            if attempt < MAX_RETRIES:

                time.sleep(
                    attempt * 1.5
                )


    raise RuntimeError(
        f"BCG request failed after "
        f"{MAX_RETRIES} attempts: "
        f"{last_error}"
    )


# ============================================================
# MAIN FETCHER
# ============================================================

def fetch_bcg(source):
    """
    Fetch Boston Consulting Group jobs from the public
    Eightfold jobs endpoint.

    The source configuration supplies:

        target
        domain
        max_pages

    Returns dictionaries compatible with monitor.py.
    """

    api_url = source["target"]

    domain = source.get(
        "domain",
        "bcg.com",
    )

    max_pages = int(
        source.get(
            "max_pages",
            150,
        )
    )


    session = requests.Session()

    session.headers.update(
        BROWSER_HEADERS
    )


    jobs_by_id = {}

    expected_total = None


    print(
        "  BCG Eightfold API:"
        f" {api_url}"
    )


    for page in range(max_pages):

        start = page * PAGE_SIZE


        data = request_page(
            session=session,
            api_url=api_url,
            domain=domain,
            start=start,
        )


        positions = data.get(
            "positions"
        )


        if not isinstance(
            positions,
            list,
        ):

            positions = []


        # ----------------------------------------------------
        # TOTAL COUNT
        # ----------------------------------------------------

        count = data.get("count")

        if (
            expected_total is None
            and isinstance(
                count,
                (int, float),
            )
        ):

            expected_total = int(count)


        # ----------------------------------------------------
        # END OF BOARD
        # ----------------------------------------------------

        if not positions:
            break


        # ----------------------------------------------------
        # NORMALIZE POSITIONS
        # ----------------------------------------------------

        for position in positions:

            if not isinstance(
                position,
                dict,
            ):
                continue


            title = get_title(
                position
            )

            if not title:
                continue


            job_id = get_job_id(
                position
            )


            url = get_job_url(
                position,
                job_id,
            )


            # We need something stable for deduplication.
            if job_id:

                global_id = (
                    f"bcg:{job_id}"
                )

            elif url:

                global_id = (
                    f"bcg:{url}"
                )

            else:

                # Without ID or URL the record is not
                # reliable enough to monitor.
                continue


            posted_raw = (
                position.get("t_create")
                or position.get("postedTs")
                or position.get("creationTs")
                or position.get("t_update")
            )


            department = (
                position.get("department")
                or position.get("business_unit")
                or position.get("businessUnit")
                or ""
            )


            jobs_by_id[global_id] = {

                "global_id": global_id,

                "title": title,

                "location": assemble_location(
                    position
                ),

                "department": str(
                    department
                ).strip(),

                "team": "",

                "posted_at": timestamp_to_string(
                    posted_raw
                ),

                "url": url,

                "apply_url": url,
            }


        # ----------------------------------------------------
        # STOP CONDITIONS
        # ----------------------------------------------------

        if len(positions) < PAGE_SIZE:
            break


        if (
            expected_total is not None
            and start + PAGE_SIZE
            >= expected_total
        ):
            break


        time.sleep(
            PAGE_PAUSE_SECONDS
        )


    jobs = list(
        jobs_by_id.values()
    )


    print(
        f"  BCG API returned "
        f"{len(jobs)} unique jobs"
    )


    if (
        expected_total is not None
        and len(jobs) < expected_total
        and max_pages * PAGE_SIZE
        < expected_total
    ):

        print(
            "  ⚠️ BCG source may be truncated: "
            f"{len(jobs)} of "
            f"{expected_total} retrieved."
        )


    return jobs
