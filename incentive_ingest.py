import requests, psycopg2
from datetime import datetime

DB_DSN = (
    "host=ep-cold-bar-ad3i9adr-pooler.c-2.us-east-1.aws.neon.tech "
    "port=5432 dbname=neondb user=neondb_owner "
    "password=npg_rD2zXVlkZG9d sslmode=require"
)
MC_KEY = "dvfpL49gNGnoM4JkBRHT8AZMewv8dpA3"

# major SoCal zips to cover roughly LA–OC–SD–IE–AV
ZIPS = ["93534", "90001", "91730", "92612", "92101"]

MAKE_GROUPS = [
    "Toyota,Honda,Nissan,Hyundai,Kia",
    "Ford,Chevrolet,GMC,Buick,Cadillac",
    "BMW,Mercedes-Benz,Audi,Volkswagen,Volvo",
    "Jeep,Ram,Dodge,Chrysler,Lincoln,Subaru,Infiniti,Lexus"
]

def fetch_incentives(zip_code, make_group):
    url = "https://api.marketcheck.com/v2/search/car/incentive/oem"
    params = {
        "api_key": MC_KEY,
        "incentive_type": "lease",
        "term_range": "36-36",
        "miles_per_year_range": "12000-12000",
        "zip": zip_code,
        "radius": 100,
        "state": "CA",
        "dealer_type": "franchise",
        "make": make_group,
        "rows": 250,
        "sort_by": "payment",
        "sort_order": "asc"
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def insert_incentives(cur, data, zip_code):
    for item in data.get("listings", []):
        offer = item.get("offer", {})
        if not offer or offer.get("offer_type") != "lease":
            continue
        v = offer["vehicles"][0]
        cur.execute("""
            INSERT INTO lease_programs
              (make, model, year, payment, due_at_signing, msrp,
               region, source, captured_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,now())
            ON CONFLICT DO NOTHING
        """, (
            v.get("make"),
            v.get("model"),
            v.get("year"),
            offer.get("amounts", [{}])[0].get("monthly"),
            offer.get("due_at_signing"),
            offer.get("msrp"),
            zip_code,
            "MarketCheck"
        ))

def update_deal_index():
    conn = psycopg2.connect(DB_DSN)
    cur = conn.cursor()
    cur.execute("""
        ALTER TABLE lease_programs
        ADD COLUMN IF NOT EXISTS deal_index numeric(10,6);
    """)
    cur.execute("""
        UPDATE lease_programs
        SET deal_index = ROUND(
            (COALESCE(payment,0) + (COALESCE(due_at_signing,0) / 36.0))
            / NULLIF(msrp,0), 6
        )
        WHERE msrp IS NOT NULL;
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("💡 deal_index updated.")


def main():
    conn = psycopg2.connect(DB_DSN)
    cur = conn.cursor()
    print("📡 Fetching incentives from MarketCheck...")

    total = 0
    for z in ZIPS:
        for mg in MAKE_GROUPS:
            try:
                data = fetch_incentives(z, mg)
                count = len(data.get("listings", []))
                print(f"{z} / {mg}: {count} listings")
                insert_incentives(cur, data, z)
                total += count
            except Exception as e:
                print(f"⚠️ {z}/{mg}: {e}")

    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Inserted {total} listings total.")
    update_deal_index()
    print("🚀 Done ingesting OEM incentives.")

if __name__ == "__main__":
    main()

