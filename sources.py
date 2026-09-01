SOURCES = [

    # ============================================================
    # INVESTMENT BANKS / FINANCIAL INSTITUTIONS
    # ============================================================

    {
        "name": "Goldman Sachs",
        "method": "ats",
        "ats": "oracle",
        "slug": "hdpc/cx_3001",
    },

    {
        "name": "JPMorgan Chase",
        "method": "ats",
        "ats": "oracle",
        "slug": "jpmc",
    },

    {
        "name": "Morgan Stanley",
        "method": "ats",
        "ats": "eightfold",
        "slug": "morganstanley",
    },

    {
        "name": "Citi",
        "method": "ats",
        "ats": "eightfold",
        "slug": "citi",
    },

    {
        "name": "HSBC",
        "method": "ats",
        "ats": "eightfold",
        "slug": "hsbc",
    },

    {
        "name": "Barclays",
        "method": "ats",
        "ats": "workday",
        "slug": "barclays/external_career_site_barclays",
    },

    {
        "name": "Deutsche Bank",
        "method": "ats",
        "ats": "smartrecruiters",
        "slug": "deutschebank",
    },

    {
        "name": "Jefferies",
        "method": "ats",
        "ats": "oracle",
        "slug": "hdid",
    },

    {
        "name": "Santander",
        "method": "ats",
        "ats": "workday",
        "slug": "santander/santandercareers",
    },

    {
        "name": "BlackRock",
        "method": "ats",
        "ats": "workday",
        "slug": "blackrock/blackrock_professional",
    },

    # Lazard was not found by company-name search,
    # but Lazard's own website links directly to this Oracle careers site.
    {
        "name": "Lazard",
        "method": "url",
        "url": (
            "https://icbpjb.fa.ocs.oraclecloud.com/"
            "hcmUI/CandidateExperience/en/sites/"
            "LazardStudentCareers/jobs"
        ),
    },
]
