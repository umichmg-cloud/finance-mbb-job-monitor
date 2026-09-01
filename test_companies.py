from ats_scrapers import find_company
from config import FIRMS


print("=" * 70)
print("TESTING ATS-SCRAPERS COMPANY DISCOVERY")
print("=" * 70)


for category, companies in FIRMS.items():

    print()
    print(f"--- {category} ---")

    for company_name in companies:

        try:

            result = find_company(company_name)

            print()
            print(f"COMPANY: {company_name}")

            if result:
                print("✅ FOUND")
                print(result)
            else:
                print("❌ NOT FOUND")

        except Exception as error:

            print()
            print(f"COMPANY: {company_name}")
            print("❌ ERROR")
            print(error)
