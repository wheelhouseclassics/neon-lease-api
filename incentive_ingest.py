import os
import requests
import psycopg2
from datetime import datetime

# --- Database connection ---
DB_DSN = (
    "host=ep-cold-bar-ad3i9adr-pooler.c-2.us-east-1.aws.neon.tech "
    "port=5432 "
    "dbname=neondb "
    "user=neondb_owner "
    "password=npg_rD2zXVlkZG9d "
    "sslmode=require"
)

# --- MarketCheck setup ---
MC_KEY = "dvfpL49gNGnoM4JkBRHT8AZMewv8dpA3"
URL = "https://api.marketcheck.com/v2/search/car/incentive/oem"

QUERY = {
    "api_key": MC_KEY,
    "incentive_type": "lease",
    "term_range": "36-36",     # 3-year leases
    "zip": "93534",            # Lancaster, CA
    "radius": 300,             # within 300 miles
    "make": (
        "Ford,Chevrolet,GMC,Buick,Cadillac,Honda,Toyota,Nissan,Lexus,Infiniti,"
        "Dodge,Ram,Jeep,Lincoln,Mercedes-Benz,BMW,Hyundai,Kia,Volkswagen,Subaru,Volvo"
    ),
    "rows": 250,
    "sort_by": "payment",
    "sort_order": "asc"
}

# --- Main functions ---
def fetch_incentives():
    """Fetch incentives from MarketCheck."""
    try:
        print("📡 Fetching incentives from MarketCheck...")
        response = requests.get(URL, params=QUERY, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")
        return None


def insert_incentives(cur, data):
    """Insert data into Neon."""
    count = 0
    for listing in data.get("listings", []):
        offer = listing.get("offer", {})
        if not offer or offer.get("offer_type") != "lease":
            continue

        vehicles = offer.get("vehicles", [])
        if not vehicles:
            continue

        v = vehicles[0]
        make = v.get("make")
        model = v.get("model")
        year = v.get("year")
        trim = v.get("trim")
        distance = listing.get("distance")

        # Incentive details
        amounts = offer.get("amounts", [])
        if not amounts:
            continue

        term = amounts[0].get("term")
        payment = amounts[0].get("monthly")
        due_at_signing = offer.get("due_at_signing")
        residual = offer.get("lease_end_purchase_price")
        msrp = offer.get("msrp")

        cur.execute("""
            INSERT INTO lease_programs (
                make, model, year, trim, term_months,
                payment, due_at_signing, residual_percent,
                msrp, distance, region, source, captured_at
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now())
            ON CONFLICT DO NOTHING
        """, (
            make, model, year, trim, term, payment,
            due_at_signing, residual, msrp,
            distance, "CA", "MarketCheck"
        ))
        count += 1

    print(f"✅ Inserted {count} records into Neon.")


def main():
    """Main entrypoint."""
    conn = psycopg2.connect(DB_DSN)
    conn.autocommit = False
    cur = conn.cursor()

    data = fetch_incentives()
    if not data:
        print("⚠️ No data returned from MarketCheck.")
        return

    insert_incentives(cur, data)
    conn.commit()
    cur.close()
    conn.close()
    print("🚀 Done ingesting OEM incentives.")


if __name__ == "__main__":
    main()

