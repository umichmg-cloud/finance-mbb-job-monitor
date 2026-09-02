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
    # Eightfold custom
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
    # Custom McKinsey fetcher
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
    # Eightfold custom
    # ------------------------------------------------------------

    {
        "name": "Boston Consulting Group",
        "category": "MBB",
        "method": "custom",
        "fetcher": "eightfold",
        "target": "https://bcg.eightfold.ai",
        "domain": "bcg.com",
        "max_pages": 200,
    },


    # ------------------------------------------------------------
    # BAIN & COMPANY
    # Custom Bain fetcher
    #
    # IMPORTANT:
    # Bain should appear ONLY ONCE.
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


    # ============================================================
    # ADDITIONAL FINANCE SOURCES
    # ============================================================


    # ------------------------------------------------------------
    # BANK OF AMERICA
    # TAL.net campus careers
    # ------------------------------------------------------------

    {
        "name": "Bank of America",
        "category": "FINANCE",
        "method": "custom",
        "fetcher": "talnet",
        "target": (
            "https://bankcampuscareers.tal.net/"
            "vx/lang-en-GB/mobile-0/brand-4/"
            "candidate/jobboard/vacancy/1/adv/"
        ),
        "page_size": 50,
        "max_pages": 6,
        "detail_location_fallback": False,
    },


    # ------------------------------------------------------------
    # UBS
    # BrassRing Graduate Board
    # ------------------------------------------------------------

    {
        "name": "UBS",
        "category": "FINANCE",
        "method": "custom",
        "fetcher": "brassring",
        "target": (
            "https://sjobs.brassring.com/"
            "TGnewUI/Search/Home/Home"
        ),
        "partner_id": "25008",
        "site_id": "5131",
    },


    # ------------------------------------------------------------
    # DEUTSCHE BANK
    # Yello / Recsolu
    # ------------------------------------------------------------

    {
        "name": "Deutsche Bank",
        "category": "FINANCE",
        "method": "custom",
        "fetcher": "yello",
        "target": (
            "https://db.recsolu.com/"
            "job_boards/DT5zqeU-qZM-ltrVsIvR9Q"
        ),
    },


    # ------------------------------------------------------------
    # EVERCORE
    # TAL.net students and graduates
    # ------------------------------------------------------------

    {
        "name": "Evercore",
        "category": "FINANCE",
        "method": "custom",
        "fetcher": "talnet",
        "target": (
            "https://evercore.tal.net/"
            "vx/lang-en-GB/mobile-0/"
            "appcentre-1/brand-6/"
            "candidate/jobboard/vacancy/2"
        ),
        "page_size": 50,
        "max_pages": 4,
        "detail_location_fallback": True,
    },


    # ------------------------------------------------------------
    # ROTHSCHILD & CO
    # TAL.net student opportunities
    # ------------------------------------------------------------

    {
        "name": "Rothschild & Co",
        "category": "FINANCE",
        "method": "custom",
        "fetcher": "talnet",
        "target": (
            "https://rothschildandco.tal.net/"
            "vx/lang-en-GB/mobile-0/"
            "appcentre-ext/brand-4/"
            "candidate/jobboard/vacancy/2/adv/"
        ),
        "page_size": 50,
        "max_pages": 4,
        "detail_location_fallback": True,
    },


    # ------------------------------------------------------------
    # MACQUARIE GROUP
    # Avature
    # ------------------------------------------------------------

    {
        "name": "Macquarie Group",
        "category": "FINANCE",
        "method": "custom",
        "fetcher": "avature",
        "target": (
            "https://recruitment.macquarie.com/"
            "en_US/careers/SearchJobs/"
        ),
        "search_params": {
            "7959": "[421070,421069]",
            "7959_format": "14495",
            "listFilterMode": "1",
        },
        "records_per_page": 50,
        "max_pages": 10,
    },

]
