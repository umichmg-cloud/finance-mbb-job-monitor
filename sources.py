    # ============================================================
    # MBB
    # ============================================================


    # ------------------------------------------------------------
    # MCKINSEY & COMPANY
    #
    # Verified current GitHub implementation:
    # Workday
    # tenant: mckinsey
    # server: wd1
    # site: McKinsey_Careers
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
    #
    # Current working GitHub implementation uses
    # BCG's public Eightfold API.
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
    #
    # Verified current GitHub implementation:
    # Workday
    # tenant: bain
    # server: wd1
    # site: External_Career_Site
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
