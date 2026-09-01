from ats_scrapers import find_company
from config import FIRMS


print("=" * 80)
print("TESTING ATS-SCRAPERS COMPANY DISCOVERY")
print("=" * 80)


for category, companies in FIRMS.items():

    print()
    print("=" * 80)
    print(f"CATEGORY: {category}")
    print("=" * 80)

    for company_name in companies:

        print()
        print(f"COMPANY: {company_name}")

        try:

            # find_company returns a pandas DataFrame
            results = find_company(company_name, limit=5)

            # A DataFrame must be checked with .empty
            if results.empty:

                print("❌ NOT FOUND IN ATS DIRECTORY")

            else:

                print(f"✅ FOUND {len(results)} MATCH(ES)")

                # Only display the useful columns
                useful_columns = [
                    col
                    for col in ["ats", "name", "slug", "url"]
                    if col in results.columns
                ]

                print(
                    results[useful_columns].to_string(
                        index=False
                    )
                )

        except Exception as error:

            print("❌ REAL ERROR")
            print(f"{type(error).__name__}: {error}")


print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
