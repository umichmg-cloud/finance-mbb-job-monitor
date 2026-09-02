SOURCES = [

    # ============================================================
    # FINANCIAL INSTITUTIONS
    # ============================================================


    # ------------------------------------------------------------
    # GOLDMAN SACHS
    # Oracle
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
    # Oracle
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
    # Eightfold
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
    # Workday
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
    # This source is currently expected to fail.
    # We will replace it later with a custom Eightfold source.
    # ------------------------------------------------------------

    {
        "name": "HSBC",
        "category": "FINANCE",
        "method": "custom",
        "fetcher": "eightfold",
        "target": "https://hsbc.eightfold.ai",
        "domain": "hsbc.com",
        "max_pages": 200,
    },

    # ------------------------------------------------------------
    # BARCLAYS
    # Workday
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
    # Oracle
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
    # Workday
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
    # Workday
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
    # Oracle Student Careers
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
    # MBB
    # ============================================================


    # ------------------------------------------------------------
    # MCKINSEY & COMPANY
    # Workday
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
    # Custom Eightfold fetcher
    # ------------------------------------------------------------

    {
        "name": "Bain & Company",
        "category": "MBB",
        "method": "custom",
        "fetcher": "bain",
        "target": (
            "https://careers.bain.com/"
            "jobs/SearchJobs"
        ),
        "max_pages": 120,
    },


    # ------------------------------------------------------------
    # BAIN & COMPANY
    # Workday
    # ------------------------------------------------------------

    {
        "name": "Bain & Company",
        "category": "MBB",
        "method": "custom",
        "fetcher": "avature",
        "target": (
            "https://careers.bain.com"
        ),
        "avature_origin": (
            "https://bain.avature.net"
        ),
        "role_terms": [
            "associate consultant",
        ],
        "max_pages": 120,
    },

]
