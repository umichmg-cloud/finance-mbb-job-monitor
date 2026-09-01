import hashlib
import json
from pathlib import Path

from ats_scrapers.scrapers import get_scraper

from sources import SOURCES


# ============================================================
# FILES
# ============================================================

DATA_DIR = Path("data")

SEEN_FILE = DATA_DIR / "seen_jobs.json"
CURRENT_FILE = DATA_DIR / "current_jobs.json"
NEW_FILE = DATA_DIR / "new_jobs.json"

DATA_DIR.mkdir(exist_ok=True)


# ============================================================
# LOCATIONS
# ============================================================

HONG_KONG_TERMS = [
    "hong kong",
    "hongkong",
    "hong kong sar",
    "hong kong s.a.r",
]

MEXICO_CITY_TERMS = [
    "mexico city",
    "ciudad de mexico",
    "ciudad de méxico",
    "cdmx",
    "mexico d.f",
    "mexico, df",
]


# ============================================================
# FINANCE ROLES WE ACTUALLY CARE ABOUT
# ============================================================

FINANCE_TERMS = [

    # Investment Banking
    "investment banking",
    "investment bank",
    "m&a",
    "mergers and acquisitions",
    "mergers & acquisitions",
    "advisory",

    # Capital Markets
    "capital markets",
    "debt capital markets",
    "equity capital markets",
    "dcm",
    "ecm",
    "leveraged finance",

    # Markets
    "global markets",
    "sales and trading",
    "sales & trading",
    "sales, trading",
    "trading",
    "equity derivatives",
    "derivatives",
    "structuring",
    "structurer",
    "ficc",
    "fixed income",
    "rates",
    "foreign exchange",
    "fx",
    "equities",

    # Research
    "equity research",
    "global investment research",
    "global research",
    "investment research",
    "credit research",

    # Asset / Wealth Management
    "asset management",
    "investment management",
    "wealth management",
    "private wealth",
    "private bank",
    "private banking",
    "private investing",

    # Corporate Banking
    "corporate banking",
    "global banking",
    "commercial & investment bank",
    "commercial and investment bank",
    "corporate & investment banking",
    "corporate and investment banking",
    "global corporate banking",
    "coverage",

    # Credit
    "credit risk",
    "credit analyst",
]


# ============================================================
# EARLY-CAREER TERMS
# ============================================================

ENTRY_LEVEL_TERMS = [
    "analyst",
    "new analyst",
    "summer analyst",
    "graduate",
    "graduate programme",
    "graduate program",
    "intern",
    "internship",
    "off cycle",
    "off-cycle",
    "seasonal",
]


# ============================================================
# SENIOR ROLES WE DON'T WANT
# ============================================================

SENIOR_TERMS = [
    "vice president",
    " vp ",
    "vp/",
    "vp -",
    "svp",
    "senior vice president",
    "executive director",
    "managing director",
    "director",
    "head of",
    "principal",
    "partner",
]


# ============================================================
# NON-TARGET FUNCTIONS
# ============================================================

IRRELEVANT_TERMS = [
    "software engineer",
    "software developer",
    "developer",
    "technology",
    "data engineer",

    "human resources",
    "recruiting",
    "recruiter",

    "legal counsel",
    "communications",

    "kyc",
    "know your customer",

    "internal audit",
    "compliance",

    "operations",
    "middle office",

    "controller",
    "controllers",

    "driver",
    "administrative assistant",
    "executive assistant",
]


# ============================================================
# MBB — FOR WHEN WE ADD MCKINSEY / BCG / BAIN
# ============================================================

MBB_TERMS = [
    "business analyst",
    "associate consultant",
    "consultant",
    "consulting",
    "associate",
    "intern",
    "internship",
]


# ============================================================
# HELPERS
# ============================================================

def get_value(job, field):
    value = getattr(job, field, None)

    if value is None:
        return ""

    return str(value).strip()


def contains_any(text, terms):
    text = text.lower()

    return any(
        term.lower() in text
        for term in terms
    )


# ============================================================
# LOCATION FILTER
# ============================================================

def classify_location(job):

    location = get_value(
        job,
        "location",
    ).lower()

    # Morgan Stanley often simply says HK
    if location.strip() == "hk":
        return "Hong Kong"

    if any(
        term in location
        for term in HONG_KONG_TERMS
    ):
        return "Hong Kong"

    if any(
        term in location
        for term in MEXICO_CITY_TERMS
    ):
        return "Mexico City"

    return None


# ============================================================
# FINANCE FILTER
# ============================================================

def is_finance_role(job):

    title = get_value(
        job,
        "title",
    )

    department = get_value(
        job,
        "department",
    )

    team = get_value(
        job,
        "team",
    )

    description = get_value(
        job,
        "description",
    )

    title_lower = title.lower()

    combined = (
        title
        + " "
        + department
        + " "
        + team
        + " "
        + description[:10000]
    ).lower()

    # --------------------------------------
    # REMOVE SENIOR POSITIONS
    # --------------------------------------

    if contains_any(
        title_lower,
        SENIOR_TERMS,
    ):
        return False

    # --------------------------------------
    # REMOVE CLEARLY IRRELEVANT FUNCTIONS
    # --------------------------------------

    if contains_any(
        title_lower,
        IRRELEVANT_TERMS,
    ):
        return False

    # --------------------------------------
    # MUST LOOK LIKE EARLY CAREER
    # --------------------------------------

    if not contains_any(
        title_lower,
        ENTRY_LEVEL_TERMS,
    ):
        return False

    # --------------------------------------
    # MUST BE FINANCE
    # --------------------------------------

    if not contains_any(
        combined,
        FINANCE_TERMS,
    ):
        return False

    return True


# ============================================================
# MBB FILTER
# ============================================================

def is_mbb_role(job):

    title = get_value(
        job,
        "title",
    ).lower()

    if contains_any(
        title,
        SENIOR_TERMS,
    ):
        return False

    if contains_any(
        title,
        IRRELEVANT_TERMS,
    ):
        return False

    return contains_any(
        title,
        MBB_TERMS,
    )


# ============================================================
# UNIQUE JOB ID
# ============================================================

def make_job_id(job, company):

    global_id = get_value(
        job,
        "global_id",
    )

    if global_id:
        return global_id

    requisition_id = get_value(
        job,
        "requisition_id",
    )

    if requisition_id:
        return (
            f"{company}:"
            f"{requisition_id}"
        )

    url = (
        get_value(job, "apply_url")
        or
        get_value(job, "url")
    )

    if url:
        return f"{company}:{url}"

    # Last-resort fallback

    raw = (
        company
        + get_value(job, "title")
        + get_value(job, "location")
    )

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()


# ============================================================
# NORMALIZE JOB
# ============================================================

def job_to_dict(
    job,
    company,
    category,
    location_group,
):

    url = (
        get_value(job, "apply_url")
        or
        get_value(job, "url")
    )

    return {
        "id": make_job_id(
            job,
            company,
        ),

        "company": company,

        "category": category,

        "title": get_value(
            job,
            "title",
        ),

        "location": get_value(
            job,
            "location",
        ),

        "location_group": location_group,

        "posted_at": get_value(
            job,
            "posted_at",
        ),

        "department": get_value(
            job,
            "department",
        ),

        "team": get_value(
            job,
            "team",
        ),

        "url": url,
    }


# ============================================================
# LOAD / SAVE STATE
# ============================================================

def load_seen():

    if not SEEN_FILE.exists():
        return set()

    try:

        data = json.loads(
            SEEN_FILE.read_text(
                encoding="utf-8"
            )
        )

        return set(data)

    except Exception:
        return set()


def save_json(path, data):

    path.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


# ============================================================
# MAIN SCRAPER
# ============================================================

def collect_jobs():

    relevant_jobs = []

    print()
    print("=" * 90)
    print("FINANCE + MBB JOB MONITOR")
    print("Hong Kong + Mexico City")
    print("=" * 90)

    for source in SOURCES:

        company = source["name"]

        category = source.get(
            "category",
            "FINANCE",
        )

        print()
        print(
            f"Checking {company}..."
        )

        try:

            scraper = get_scraper(
                source["ats"],
                source["target"],
            )

            jobs = scraper.fetch()

            print(
                f"  Retrieved: {len(jobs)}"
            )

            company_matches = 0

            for job in jobs:

                location_group = (
                    classify_location(job)
                )

                if not location_group:
                    continue

                if category == "MBB":

                    if not is_mbb_role(job):
                        continue

                else:

                    if not is_finance_role(job):
                        continue

                relevant_jobs.append(
                    job_to_dict(
                        job,
                        company,
                        category,
                        location_group,
                    )
                )

                company_matches += 1

            print(
                f"  Relevant: {company_matches}"
            )

        except Exception as error:

            print(
                f"  ❌ FAILED: "
                f"{type(error).__name__}: "
                f"{error}"
            )

    return relevant_jobs


# ============================================================
# RUN
# ============================================================

def main():

    first_run = not SEEN_FILE.exists()

    seen = load_seen()

    jobs = collect_jobs()

    # Remove accidental duplicates
    unique_jobs = {
        job["id"]: job
        for job in jobs
    }

    jobs = list(
        unique_jobs.values()
    )

    # Sort nicely
    jobs.sort(
        key=lambda x: (
            x["location_group"],
            x["company"],
            x["title"],
        )
    )

    if first_run:

        # IMPORTANT:
        #
        # On the first ever run, all existing
        # vacancies become the baseline.
        #
        # We do NOT call them "new".
        new_jobs = []

    else:

        new_jobs = [
            job
            for job in jobs
            if job["id"] not in seen
        ]

    # Add currently active roles to history
    for job in jobs:
        seen.add(
            job["id"]
        )

    save_json(
        CURRENT_FILE,
        jobs,
    )

    save_json(
        NEW_FILE,
        new_jobs,
    )

    save_json(
        SEEN_FILE,
        sorted(seen),
    )


    print()
    print("=" * 90)
    print("RESULT")
    print("=" * 90)

    print(
        f"Relevant active jobs: "
        f"{len(jobs)}"
    )

    print(
        f"NEW jobs since last run: "
        f"{len(new_jobs)}"
    )


    if first_run:

        print()
        print(
            "FIRST RUN: existing jobs have "
            "been saved as the baseline."
        )

        print(
            "They will NOT be treated as new."
        )


    if new_jobs:

        print()
        print("🚨 NEW JOBS")
        print("=" * 90)

        for job in new_jobs:

            print()
            print(
                f"{job['company']}"
            )

            print(
                f"{job['title']}"
            )

            print(
                f"📍 {job['location']}"
            )

            if job["posted_at"]:

                print(
                    f"Posted: "
                    f"{job['posted_at']}"
                )

            print(
                job["url"]
            )


if __name__ == "__main__":
    main()
