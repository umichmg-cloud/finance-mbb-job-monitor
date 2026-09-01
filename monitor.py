import hashlib
import json
import re
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

    # --------------------------------------------------------
    # INVESTMENT BANKING
    # --------------------------------------------------------

    "investment banking",
    "investment bank",
    "global investment banking",
    "m&a",
    "mergers and acquisitions",
    "mergers & acquisitions",
    "financial advisory",

    # --------------------------------------------------------
    # CAPITAL MARKETS
    # --------------------------------------------------------

    "capital markets",
    "debt capital markets",
    "equity capital markets",
    "dcm",
    "ecm",
    "leveraged finance",

    # --------------------------------------------------------
    # MARKETS
    # --------------------------------------------------------

    "global markets",
    "markets analyst",
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

    # --------------------------------------------------------
    # RESEARCH
    # --------------------------------------------------------

    "equity research",
    "global investment research",
    "global research",
    "investment research",
    "credit research",

    # --------------------------------------------------------
    # ASSET MANAGEMENT / WEALTH
    # --------------------------------------------------------

    "asset management",
    "investment management",
    "wealth management",
    "private wealth",
    "private bank",
    "private banking",
    "private investing",
    "portfolio management",

    # --------------------------------------------------------
    # CORPORATE BANKING / COVERAGE
    # --------------------------------------------------------

    "corporate banking",
    "global banking",
    "global corporate banking",
    "commercial & investment bank",
    "commercial and investment bank",
    "corporate & investment banking",
    "corporate and investment banking",
    "coverage",
    "subsidiary banking",

    # --------------------------------------------------------
    # CREDIT / INVESTMENT RISK
    # --------------------------------------------------------

    "credit risk",
    "credit analyst",
    "investment risk",

    # --------------------------------------------------------
    # OTHER RELEVANT FRONT-OFFICE AREAS
    # --------------------------------------------------------

    "private equity",
    "prime synthetics",
]


# ============================================================
# EARLY-CAREER PATTERNS
# ============================================================
#
# Regex is used here rather than simple substring matching.
#
# This prevents:
#
# "intern"
#
# from incorrectly matching:
#
# "International"
#
# ============================================================

ENTRY_LEVEL_PATTERNS = [

    r"\bnew analyst\b",

    r"\bsummer analyst\b",

    r"\bfull[- ]time analyst\b",

    r"\banalyst program\b",

    r"\banalyst programme\b",

    r"\bgraduate program\b",

    r"\bgraduate programme\b",

    r"\binternship\b",

    r"\bintern\b",

    r"\boff[- ]cycle\b",

    r"\bseasonal\b",

    # Generic analyst-level positions
    r"\banalyst\b",
]


# ============================================================
# SENIOR ROLES WE DO NOT WANT
# ============================================================

SENIOR_PATTERNS = [

    # Broad protection against senior titles
    r"\bsenior\b",

    r"\bsr\.?\s*analyst\b",

    # Banking hierarchy
    r"\bavp\b",
    r"\bvp\b",
    r"\bsvp\b",

    r"\bvice president\b",
    r"\bsenior vice president\b",

    r"\bexecutive director\b",
    r"\bmanaging director\b",

    r"\bdirector\b",

    r"\bhead of\b",

    r"\bprincipal\b",

    r"\bpartner\b",
]


# ============================================================
# FUNCTIONS WE DO NOT WANT
# ============================================================

IRRELEVANT_TERMS = [

    # --------------------------------------------------------
    # TECHNOLOGY
    # --------------------------------------------------------

    "software engineer",
    "software developer",
    "full stack developer",
    "developer",
    "data engineer",
    "applications support",
    "application support",
    "technology support",
    "production support",

    # --------------------------------------------------------
    # OPERATIONS / MIDDLE OFFICE
    # --------------------------------------------------------

    "trade support",
    "middle office",
    "operations",
    "client onboarding",
    "settlements",
    "reconciliation",

    # --------------------------------------------------------
    # COMPLIANCE / AML
    # --------------------------------------------------------

    "kyc",
    "know your customer",
    "aml",
    "anti-money laundering",
    "compliance",
    "internal audit",

    # --------------------------------------------------------
    # CORPORATE / FINANCE SUPPORT
    # --------------------------------------------------------

    "controller",
    "controllers",
    "data analyst",
    "fp&a",
    "financial planning",

    # --------------------------------------------------------
    # HR / LEGAL / COMMUNICATIONS
    # --------------------------------------------------------

    "human resources",
    "recruiting",
    "recruiter",
    "legal counsel",
    "communications",

    # --------------------------------------------------------
    # OBVIOUSLY IRRELEVANT
    # --------------------------------------------------------

    "driver",
    "administrative assistant",
    "executive assistant",
]


# ============================================================
# MBB ROLE PATTERNS
# ============================================================
#
# These are not active until MBB sources are added to
# sources.py with:
#
# "category": "MBB"
#
# ============================================================

MBB_PATTERNS = [

    r"\bbusiness analyst\b",

    r"\bassociate consultant\b",

    r"\bconsultant\b",

    r"\bconsulting\b",

    r"\bassociate\b",

    r"\bintern\b",

    r"\binternship\b",
]


# ============================================================
# HELPERS
# ============================================================

def get_value(job, field):
    """
    Safely obtain a value from an ats-scrapers Job object.
    """

    value = getattr(job, field, None)

    if value is None:
        return ""

    return str(value).strip()


def contains_any(text, terms):
    """
    Simple case-insensitive substring matching.
    """

    text = text.lower()

    return any(
        term.lower() in text
        for term in terms
    )


def matches_any_pattern(text, patterns):
    """
    Regex-based matching.

    Useful for words such as:

    intern
    analyst
    VP

    where simple substring matching can produce
    false positives.
    """

    return any(
        re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )
        for pattern in patterns
    )


# ============================================================
# LOCATION FILTER
# ============================================================

def classify_location(job):
    """
    Return:

    Hong Kong
    Mexico City
    None

    Only the structured ATS location field is used.
    """

    location = get_value(
        job,
        "location",
    ).lower()


    # --------------------------------------------------------
    # HONG KONG
    # --------------------------------------------------------

    # Morgan Stanley frequently just says "HK"
    if location.strip() == "hk":
        return "Hong Kong"

    if any(
        term in location
        for term in HONG_KONG_TERMS
    ):
        return "Hong Kong"


    # --------------------------------------------------------
    # MEXICO CITY
    # --------------------------------------------------------

    if any(
        term in location
        for term in MEXICO_CITY_TERMS
    ):
        return "Mexico City"


    return None


# ============================================================
# FINANCE ROLE FILTER
# ============================================================

def is_finance_role(job):
    """
    Decide whether a bank job is relevant.

    Order:

    1. Remove senior jobs
    2. Remove stale programs
    3. Remove irrelevant functions
    4. Require entry-level seniority
    5. Require relevant finance function
    """

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

    title_lower = title.lower()


    # ========================================================
    # 1. REMOVE SENIOR POSITIONS
    # ========================================================

    if matches_any_pattern(
        title_lower,
        SENIOR_PATTERNS,
    ):
        return False


    # ========================================================
    # 2. REMOVE EXPLICITLY OLD PROGRAMS
    # ========================================================
    #
    # Example:
    #
    # "2025 Corporate Banking Full Time Analyst Program"
    #
    # We DON'T care when the job was posted.
    #
    # We only remove it if the TITLE explicitly says
    # 2025 or earlier.
    #
    # ========================================================

    old_year = re.search(
        r"\b20(?:1\d|2[0-5])\b",
        title_lower,
    )

    if old_year:
        return False


    # ========================================================
    # 3. REMOVE IRRELEVANT FUNCTIONS
    # ========================================================

    if contains_any(
        title_lower,
        IRRELEVANT_TERMS,
    ):
        return False


    # ========================================================
    # 4. REQUIRE ENTRY-LEVEL SENIORITY
    # ========================================================

    if not matches_any_pattern(
        title_lower,
        ENTRY_LEVEL_PATTERNS,
    ):
        return False


    # ========================================================
    # 5. REQUIRE RELEVANT FINANCE FUNCTION
    # ========================================================
    #
    # IMPORTANT:
    #
    # We deliberately DO NOT use the complete job description.
    #
    # Descriptions often contain generic phrases such as:
    #
    # "supporting Investment Banking and Global Markets"
    #
    # which caused irrelevant jobs to become false positives.
    #
    # Title + department + team are much cleaner.
    #
    # ========================================================

    finance_text = (
        title
        + " "
        + department
        + " "
        + team
    ).lower()


    if not contains_any(
        finance_text,
        FINANCE_TERMS,
    ):
        return False


    return True


# ============================================================
# MBB ROLE FILTER
# ============================================================

def is_mbb_role(job):
    """
    Filter MBB jobs once McKinsey / BCG / Bain
    are added to sources.py.
    """

    title = get_value(
        job,
        "title",
    )

    title_lower = title.lower()


    # Remove senior consulting roles
    if matches_any_pattern(
        title_lower,
        SENIOR_PATTERNS,
    ):
        return False


    # Remove irrelevant corporate roles
    if contains_any(
        title_lower,
        IRRELEVANT_TERMS,
    ):
        return False


    # Remove explicitly old programs
    old_year = re.search(
        r"\b20(?:1\d|2[0-5])\b",
        title_lower,
    )

    if old_year:
        return False


    return matches_any_pattern(
        title_lower,
        MBB_PATTERNS,
    )


# ============================================================
# UNIQUE JOB ID
# ============================================================

def make_job_id(job, company):
    """
    Create a stable identifier so we can tell whether
    we have already seen a job.
    """

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
        get_value(
            job,
            "apply_url",
        )
        or
        get_value(
            job,
            "url",
        )
    )

    if url:
        return f"{company}:{url}"


    # --------------------------------------------------------
    # LAST-RESORT FALLBACK
    # --------------------------------------------------------

    raw = (
        company
        + "|"
        + get_value(
            job,
            "title",
        )
        + "|"
        + get_value(
            job,
            "location",
        )
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
    """
    Convert different ATS job formats into one consistent
    dictionary.
    """

    url = (
        get_value(
            job,
            "apply_url",
        )
        or
        get_value(
            job,
            "url",
        )
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
# LOAD STATE
# ============================================================

def load_seen():
    """
    Load every job ID the monitor has ever seen.
    """

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


# ============================================================
# SAVE JSON
# ============================================================

def save_json(path, data):
    """
    Save formatted JSON.
    """

    path.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


# ============================================================
# COLLECT JOBS
# ============================================================

def collect_jobs():
    """
    Fetch all configured sources and return only the jobs
    that match:

    Hong Kong / Mexico City
             +
    target finance / MBB function
             +
    appropriate seniority
    """

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

            # ------------------------------------------------
            # CREATE SCRAPER
            # ------------------------------------------------

            scraper = get_scraper(
                source["ats"],
                source["target"],
            )


            # ------------------------------------------------
            # FETCH ALL LIVE JOBS
            # ------------------------------------------------

            jobs = scraper.fetch()


            print(
                f"  Retrieved: {len(jobs)}"
            )


            company_matches = 0


            # ------------------------------------------------
            # FILTER JOBS
            # ------------------------------------------------

            for job in jobs:

                # --------------------------------------------
                # LOCATION
                # --------------------------------------------

                location_group = (
                    classify_location(job)
                )

                if not location_group:
                    continue


                # --------------------------------------------
                # ROLE
                # --------------------------------------------

                if category == "MBB":

                    if not is_mbb_role(job):
                        continue

                else:

                    if not is_finance_role(job):
                        continue


                # --------------------------------------------
                # ADD RESULT
                # --------------------------------------------

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
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # IS THIS THE FIRST EVER RUN?
    # --------------------------------------------------------

    first_run = not SEEN_FILE.exists()


    # --------------------------------------------------------
    # LOAD HISTORY
    # --------------------------------------------------------

    seen = load_seen()


    # --------------------------------------------------------
    # COLLECT CURRENT RELEVANT JOBS
    # --------------------------------------------------------

    jobs = collect_jobs()


    # --------------------------------------------------------
    # REMOVE ACCIDENTAL DUPLICATES
    # --------------------------------------------------------

    unique_jobs = {
        job["id"]: job
        for job in jobs
    }

    jobs = list(
        unique_jobs.values()
    )


    # --------------------------------------------------------
    # SORT OUTPUT NICELY
    # --------------------------------------------------------

    jobs.sort(
        key=lambda x: (
            x["location_group"],
            x["company"],
            x["title"],
        )
    )


    # --------------------------------------------------------
    # DETECT NEW JOBS
    # --------------------------------------------------------

    if first_run:

        # First run establishes the baseline.
        new_jobs = []

    else:

        new_jobs = [
            job
            for job in jobs
            if job["id"] not in seen
        ]


    # --------------------------------------------------------
    # UPDATE HISTORY
    # --------------------------------------------------------

    for job in jobs:

        seen.add(
            job["id"]
        )


    # --------------------------------------------------------
    # SAVE RESULTS
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # FIRST RUN INFORMATION
    # --------------------------------------------------------

    if first_run:

        print()

        print(
            "FIRST RUN: existing jobs have "
            "been saved as the baseline."
        )

        print(
            "They will NOT be treated as new."
        )


    # --------------------------------------------------------
    # DISPLAY NEW JOBS
    # --------------------------------------------------------

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


# ============================================================
# START PROGRAM
# ============================================================

if __name__ == "__main__":
    main()
