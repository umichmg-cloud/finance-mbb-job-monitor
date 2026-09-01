SOURCES = [

    # ============================================================
    # FINANCIAL INSTITUTIONS
    # ============================================================
    #
    # IMPORTANT:
    #
    # "target" does NOT always mean a simple company slug.
    #
    # Workday and Oracle require their COMPLETE careers URL.
    # Other ATS platforms may use a normal company slug.
    #
    # We deliberately pin these ourselves instead of relying on
    # fuzzy company-name discovery.
    # ============================================================


    # ------------------------------------------------------------
    # GOLDMAN SACHS
    # Oracle
    # ------------------------------------------------------------

    {
        "name": "Goldman Sachs",
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
        "ats": "oracle",
        "target": (
            "https://jpmc.fa.oraclecloud.com/"
            "hcmUI/CandidateExperience/en/sites/CX_1001"
        ),
    },


    # ------------------------------------------------------------
    # MORGAN STANLEY
    # Eightfold
    #
    # This already worked in our previous live test.
    # ------------------------------------------------------------

    {
        "name": "Morgan Stanley",
        "ats": "eightfold",
        "target": "morganstanley",
    },


    # ------------------------------------------------------------
    # CITI
    #
    # Eightfold partly worked but returned HTTP 405 after
    # thousands of jobs.
    #
    # The company directory also identified this Workday tenant,
    # so we test the Workday source instead.
    # ------------------------------------------------------------

    {
        "name": "Citi",
        "ats": "workday",
        "target": (
            "https://citi.wd5.myworkdayjobs.com/2"
        ),
    },


    # ------------------------------------------------------------
    # HSBC
    #
    # Eightfold returned HTTP 405 immediately.
    #
    # The company directory also identified HSBC's legacy
    # SuccessFactors careers system, so we use that instead.
    # ------------------------------------------------------------

    {
        "name": "HSBC",
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
        "ats": "workday",
        "target": (
            "https://blackrock.wd1.myworkdayjobs.com/"
            "blackrock_professional"
        ),
    },


    # ------------------------------------------------------------
    # LAZARD STUDENT CAREERS
    #
    # We already know the platform is Oracle.
    # Therefore we bypass automatic URL detection entirely.
    # ------------------------------------------------------------

    {
        "name": "Lazard",
        "ats": "oracle",
        "target": (
            "https://icbpjb.fa.ocs.oraclecloud.com/"
            "hcmUI/CandidateExperience/en/sites/"
            "LazardStudentCareers/jobs"
        ),
    },

]
{
    "name": "McKinsey & Company",
    "category": "MBB",
    "method": "ats",
    "ats": "workday",
    "target": (
        "https://mckinsey.wd3.myworkdayjobs.com/"
        "McKinsey_Externals"
    ),
},
