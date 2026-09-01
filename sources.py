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
        "method": "ats",
        "ats": "successfactors",
        "target": (
            "https://career2.successfactors.eu/"
            "career?company=hsbcholdin"
        ),
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
        "method": "ats",
        "ats": "workday",
        "target": (
            "https://mckinsey.wd1.myworkdayjobs.com/"
            "McKinsey_Careers"
        ),
    },


    # ------------------------------------------------------------
    # BOSTON CONSULTING GROUP
    # Custom Eightfold fetcher
    # ------------------------------------------------------------

    {
        "name": "Boston Consulting Group",
        "category": "MBB",
        "method": "custom",
        "fetcher": "bcg",
        "target": (
            "https://careers.bcg.com/"
            "api/apply/v2/jobs"
        ),
        "domain": "bcg.com",
        "max_pages": 150,
    },


    # ------------------------------------------------------------
    # BAIN & COMPANY
    # Workday
    # ------------------------------------------------------------

    {
        "name": "Bain & Company",
        "category": "MBB",
        "method": "ats",
        "ats": "workday",
        "target": (
            "https://bain.wd1.myworkdayjobs.com/"
            "External_Career_Site"
        ),
    },

]
