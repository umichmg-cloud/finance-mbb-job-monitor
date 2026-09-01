SOURCES = [

    # ============================================================
    # FINANCE — ATS-SCRAPERS
    # ============================================================


    # ------------------------------------------------------------
    # GOLDMAN SACHS
    # ------------------------------------------------------------

    {
        "name": "Goldman Sachs",
        "category": "FINANCE",
        "method": "ats",
        "ats": "oracle",
        "target": (
            "https://hdpc.fa.us2.oraclecloud.com/"
            "hcmUI/CandidateExperience/en/sites/cx_3001"
        ),
    },


    # ------------------------------------------------------------
    # JPMORGAN CHASE
    # ------------------------------------------------------------

    {
        "name": "JPMorgan Chase",
        "category": "FINANCE",
        "method": "ats",
        "ats": "oracle",
        "target": (
            "https://jpmc.fa.oraclecloud.com/"
            "hcmUI/CandidateExperience/en/sites/CX_1001"
        ),
    },


    # ------------------------------------------------------------
    # MORGAN STANLEY
    # ------------------------------------------------------------

    {
        "name": "Morgan Stanley",
        "category": "FINANCE",
        "method": "ats",
        "ats": "eightfold",
        "target": "morganstanley",
    },


    # ------------------------------------------------------------
    # CITI
    # ------------------------------------------------------------

    {
        "name": "Citi",
        "category": "FINANCE",
        "method": "ats",
        "ats": "workday",
        "target": (
            "https://citi.wd5.myworkdayjobs.com/2"
        ),
    },


    # ------------------------------------------------------------
    # HSBC
    #
    # This source currently fails.
    # We keep it here temporarily and will replace it with
    # a custom Eightfold fetcher later.
    # ------------------------------------------------------------

    {
        "name": "HSBC",
        "category": "FINANCE",
        "method": "ats",
        "ats": "successfactors",
        "target": (
            "https://career2.successfactors.eu/"
            "career?company=hsbcholdin"
        ),
    },


    # ------------------------------------------------------------
    # BARCLAYS
    # ------------------------------------------------------------

    {
        "name": "Barclays",
        "category": "FINANCE",
        "method": "ats",
        "ats": "workday",
        "target": (
            "https://barclays.wd3.myworkdayjobs.com/"
            "external_career_site_barclays"
        ),
    },


    # ------------------------------------------------------------
    # JEFFERIES
    # ------------------------------------------------------------

    {
        "name": "Jefferies",
        "category": "FINANCE",
        "method": "ats",
        "ats": "oracle",
        "target": (
            "https://hdid.fa.us2.oraclecloud.com/"
            "hcmUI/CandidateExperience/en/sites/CX_1"
        ),
    },


    # ------------------------------------------------------------
    # SANTANDER
    # ------------------------------------------------------------

    {
        "name": "Santander",
        "category": "FINANCE",
        "method": "ats",
        "ats": "workday",
        "target": (
            "https://santander.wd3.myworkdayjobs.com/"
            "santandercareers"
        ),
    },


    # ------------------------------------------------------------
    # BLACKROCK
    # ------------------------------------------------------------

    {
        "name": "BlackRock",
        "category": "FINANCE",
        "method": "ats",
        "ats": "workday",
        "target": (
            "https://blackrock.wd1.myworkdayjobs.com/"
            "blackrock_professional"
        ),
    },


    # ------------------------------------------------------------
    # LAZARD
    # ------------------------------------------------------------

    {
        "name": "Lazard",
        "category": "FINANCE",
        "method": "ats",
        "ats": "oracle",
        "target": (
            "https://icbpjb.fa.ocs.oraclecloud.com/"
            "hcmUI/CandidateExperience/en/sites/"
            "LazardStudentCareers/jobs"
        ),
    },


    # ============================================================
    # MBB — CUSTOM FETCHERS
    # ============================================================
    #
    # These do NOT go through ats-scrapers.
    #
    # We will create:
    #
    # custom_fetchers/mckinsey.py
    # custom_fetchers/bcg.py
    # custom_fetchers/avature.py
    #
    # ============================================================


    # ------------------------------------------------------------
    # MCKINSEY & COMPANY
    # ------------------------------------------------------------

    {
        "name": "McKinsey & Company",
        "category": "MBB",
        "method": "custom",
        "fetcher": "mckinsey",
        "target": (
            "https://www.mckinsey.com/"
            "careers/search-jobs"
        ),
    },


    # ------------------------------------------------------------
    # BOSTON CONSULTING GROUP
    #
    # BCG uses Phenom.
    # ------------------------------------------------------------

    {
        "name": "Boston Consulting Group",
        "category": "MBB",
        "method": "custom",
        "fetcher": "bcg",
        "target": (
            "https://careers.bcg.com/"
            "global/en/search-results"
        ),
    },


    # ------------------------------------------------------------
    # BAIN & COMPANY
    #
    # Bain uses Avature.
    # ------------------------------------------------------------

    {
        "name": "Bain & Company",
        "category": "MBB",
        "method": "custom",
        "fetcher": "avature",
        "target": (
            "https://bain.avature.net"
        ),
    },

]
