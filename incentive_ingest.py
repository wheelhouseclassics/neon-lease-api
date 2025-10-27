import requests
import psycopg2
from datetime import datetime
import time

DB_DSN = (
    "host=ep-cold-bar-ad3i9adr-pooler.c-2.us-east-1.aws.neon.tech "
    "port=5432 "
    "dbname=neondb "
    "user=neondb_owner "
    "password=npg_rD2zXVlkZG9d "
    "sslmode=require"
)
MC_KEY = "dvfpL49gNGnoM4JkBRHT8AZMewv8dpA3"
URL = "https://api.marketcheck.com/v2/search/car/incentive/oem"

# regional coverage
ZIPS = ["93534", "90001", "91730", "92612", "92101"]  # Lancaster, LA, Rancho, Irvine, San Diego

# make groups to keep results focused
MAKE_GROUPS = [
    "Toyota,Honda,Nissan,Hyundai,Kia",
    "Ford,Chevrolet,GMC,Buick,Cadillac",
    "BMW,Mercedes-Benz,Audi,Volkswagen,Volvo",
    "Jeep,Ram,Dodge,Chrysler,Lincoln"
]

BASE_QUERY = {
    "api_key": MC_KEY,
    "incentive_type": "lease",
    "term_range": "36-36",
    "radius": 100,
    "rows": 100,
    "sort_by": "payment",
    "sort_order": "asc"
}


def fetch_incentives(q):
    """Hit MarketCheck API and return JSON."""
    r = requests.get(URL, params=q, timeout=45)
    r.raise_for_status()
    return r.json()


def insert_incentives(cur, data, region):
    """Insert API results into Neon."""
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
                make, model, year, trim, term_months, payment,
                due_at_signing, residual_percent, msrp, distance,
                region, source, captured_at
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now())
            ON CONFLICT DO NOTHING
        """, (
            make, model, year, trim, term, payment,
            due_at_signing, residual, msrp, distance,
            region, "MarketCheck"
        ))
        count += 1
    print(f"✅ Inserted {count} rows for {region}.")


def main():
    conn = psycopg2.connect(DB_DSN)
    conn.autocommit = False
    cur = conn.cursor()

    total = 0
    for z in ZIPS:
        for makes in MAKE_GROUPS:
            q = BASE_QUERY.copy()
            q.update({"zip": z, "make": makes})
            try:
                data = fetch_incentives(q)
                found = data.get("num_found", 0)
                print(f"📡 {z} {makes.split(',')[0]}... found {found}")
                insert_incentives(cur, data, z)
                conn.commit()
                total += found
            except requests.exceptions.RequestException as e:
                print(f"❌ Request failed for {z}/{makes}: {e}")
            time.sleep(1.2)  # polite delay

    cur.close()
    conn.close()
    print(f"🚀 Complete. Total reported results: {total}")


if __name__ == "__main__":
    main()
