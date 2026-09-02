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
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def _clean(value):

    if value is None:
        return ""

    return str(value).strip()


def _hidden_input(soup, name):

    element = soup.find(
        "input",
        attrs={
            "name": name,
        },
    )

    if not element:
        return ""

    return _clean(
        element.get("value")
    )


def _question(item, name):

    questions = item.get(
        "Questions",
        [],
    )

    if not isinstance(
        questions,
        list,
    ):
        return ""


    wanted = name.lower()


    for question in questions:

        if not isinstance(
            question,
            dict,
        ):
            continue


        current = _clean(
            question.get(
                "QuestionName"
            )
        ).lower()


        if current == wanted:

            return _clean(
                question.get(
                    "Value"
                )
            )


    return ""


def _location(item):

    direct = _question(
        item,
        "location",
    )

    if direct:
        return direct


    city = _question(
        item,
        "city",
    )

    state = _question(
        item,
        "state",
    )

    country = _question(
        item,
        "country",
    )


    combined = ", ".join(
        value
        for value in [
            city,
            state,
            country,
        ]
        if value
    )


    if combined:
        return combined


    # BrassRing occasionally includes location
    # inside the job title.

    title = _question(
        item,
        "jobtitle",
    )


    if " - " in title:

        return (
            title.split(" - ")[-1]
            .strip()
        )


    return ""


def fetch_brassring(source):

    board_url = source[
        "target"
    ]


    partner_id = str(
        source["partner_id"]
    )

    site_id = str(
        source["site_id"]
    )


    parsed = urlparse(
        board_url
    )


    origin = (
        f"{parsed.scheme}://"
        f"{parsed.netloc}"
    )


    api_url = (
        origin
        + "/TgNewUI/"
        "Search/Ajax/MatchedJobs"
    )


    session = requests.Session()

    session.headers.update(
        HEADERS
    )


    print(
        "  BrassRing board: "
        f"{board_url}"
    )


    # ========================================================
    # STEP 1
    # ESTABLISH SESSION
    # ========================================================

    response = session.get(
        board_url,
        timeout=REQUEST_TIMEOUT,
        allow_redirects=True,
    )

    response.raise_for_status()


    print(
        "  BrassRing final host: "
        f"{response.url}"
    )


    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )


    verification_token = (
        _hidden_input(
            soup,
            "__RequestVerificationToken",
        )
    )


    encrypted_session = (
        _hidden_input(
            soup,
            "CookieValue",
        )
    )


    rft = (
        verification_token
        or _hidden_input(
            soup,
            "hdRft",
        )
    )


    # ========================================================
    # STEP 2
    # MATCHED JOBS API
    # ========================================================

    payload = {

        "PartnerId":
            partner_id,

        "SiteId":
            site_id,

        "Keyword":
            "",

        "Location":
            "",

        "LocationCustomSolrFields":
            "Location",

        "FacetFilterFields":
            None,

        "TurnOffHttps":
            False,

        "Latitude":
            0,

        "Longitude":
            0,

        "PowerSearchOptions": {
            "PowerSearchOption": [],
        },

        "encryptedsessionvalue":
            encrypted_session,
    }


    headers = {

        "Accept":
            "application/json, "
            "text/javascript, */*; q=0.01",

        "Content-Type":
            "application/json; charset=utf-8",

        "Origin":
            origin,

        "Referer":
            board_url,

        "X-Requested-With":
            "XMLHttpRequest",

        "User-Agent":
            HEADERS["User-Agent"],
    }


    if rft:

        headers["RFT"] = rft


    result = session.post(
        api_url,
        json=payload,
        headers=headers,
        timeout=REQUEST_TIMEOUT,
    )


    result.raise_for_status()


    data = result.json()


    rows = (
        data
        .get("Jobs", {})
        .get("Job", [])
    )


    if isinstance(rows, dict):

        rows = [rows]


    if not isinstance(rows, list):

        rows = []


    print(
        "  BrassRing API returned: "
        f"{len(rows)} jobs"
    )


    # ========================================================
    # NORMALIZE
    # ========================================================

    jobs = []


    for item in rows:

        if not isinstance(
            item,
            dict,
        ):
            continue


        title = _question(
            item,
            "jobtitle",
        )


        if not title:
            continue


        req_id = _question(
            item,
            "reqid",
        )


        location = _location(
            item
        )


        if not location:
            continue


        direct_link = _clean(
            item.get("Link")
        )


        if direct_link:

            url = urljoin(
                board_url,
                direct_link,
            )

        elif req_id:

            url = (
                origin
                + "/TGnewUI/Search/"
                "Home/Home"
                "?PageType=JobDetails"
                f"&jobid={req_id}"
                f"&partnerid={partner_id}"
                f"&siteid={site_id}"
            )

        else:

            url = board_url


        stable_id = (
            req_id
            or url
        )


        jobs.append(
            {

                "global_id":
                    (
                        "brassring:"
                        "UBS:"
                        f"{stable_id}"
                    ),

                "title":
                    title,

                "location":
                    location,

                "posted_at":
                    _question(
                        item,
                        "lastupdated",
                    ),

                "department":
                    _question(
                        item,
                        "department",
                    ),

                "team":
                    "",

                "url":
                    url,

                "apply_url":
                    url,
            }
        )


    print(
        "  BrassRing normalized: "
        f"{len(jobs)} jobs"
    )


    return jobs
