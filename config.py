FIRMS = {
    "MBB": [
        "McKinsey & Company",
        "Boston Consulting Group",
        "Bain & Company",
    ],

    "FINANCE": [
        "Goldman Sachs",
        "JPMorgan Chase",
        "Morgan Stanley",
        "Bank of America",
        "Citi",
        "UBS",
        "HSBC",
        "Barclays",
        "Deutsche Bank",
        "Lazard",
        "Evercore",
        "Rothschild & Co",
        "Jefferies",
        "Macquarie Group",
        "Santander",
        "BlackRock",
    ],
}


# --------------------------------------------------
# LOCATIONS WE WANT
# --------------------------------------------------

LOCATION_TERMS = [
    # Hong Kong
    "hong kong",
    "hongkong",
    "hong kong sar",
    "hong kong s.a.r",
    "hksar",

    # Mexico City
    "mexico city",
    "ciudad de mexico",
    "ciudad de méxico",
    "cdmx",
    "mexico d.f",
    "mexico, df",
    "santa fe",
]


# --------------------------------------------------
# FINANCE ROLES WE WANT
# --------------------------------------------------

FINANCE_TERMS = [
    # Investment Banking
    "investment banking",
    "investment bank",
    "ibd",
    "m&a",
    "mergers and acquisitions",
    "mergers & acquisitions",

    # Coverage / Corporate Banking
    "global banking",
    "corporate banking",
    "corporate & investment banking",
    "corporate and investment banking",
    "cib",
    "coverage",

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
    "trading",
    "trader",
    "structuring",
    "structurer",
    "rates",
    "foreign exchange",
    "fx",
    "fixed income",

    # Research
    "equity research",
    "global research",
    "investment research",
    "credit research",
    "research analyst",

    # Investing / Asset Management
    "asset management",
    "investment management",
    "wealth management",
    "private banking",
    "private wealth",

    # Generic finance
    "corporate finance",
    "investment analyst",
    "financial analyst",
    "advisory",
    "securities",
]


# --------------------------------------------------
# CONSULTING ROLES WE WANT
# --------------------------------------------------

CONSULTING_TERMS = [
    "business analyst",
    "associate consultant",
    "associate",
    "consultant",
    "consulting",
    "generalist",
    "intern",
    "internship",
]


# --------------------------------------------------
# REMOVE OBVIOUSLY SENIOR JOBS
# --------------------------------------------------

EXCLUDE_TERMS = [
    "managing director",
    "executive director",
    "vice president",
    "director",
    "principal",
    "partner",
    "head of",
]
