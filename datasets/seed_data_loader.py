"""
Creates all demo schema tables and inserts a small amount of seed data.

Run once after setting up your Supabase instance:
    python -m datasets.seed_data_loader

The seed data is intentionally small (a few dozen rows per table) so the
setup runs quickly. For benchmarking with larger data, swap in the full
TPC-H or NYC Taxi public datasets.
"""

from __future__ import annotations

import os
import psycopg2

from api.config import settings

SCHEMA_FILES = [
    "datasets/northwind_schema.sql",
    "datasets/tpch_schema.sql",
    "datasets/nyc_taxi_schema.sql",
]


def create_tables(conn: psycopg2.extensions.connection) -> None:
    for path in SCHEMA_FILES:
        if not os.path.exists(path):
            print(f"  Schema file not found, skipping: {path}")
            continue
        with open(path) as f:
            sql = f.read()
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        print(f"  Created tables from {path}")


def seed_northwind(conn: psycopg2.extensions.connection) -> None:
    with conn.cursor() as cur:
        cur.execute("TRUNCATE nw_order_details, nw_orders, nw_products, nw_customers, nw_employees, nw_shippers, nw_suppliers, nw_categories RESTART IDENTITY CASCADE")

        cur.execute("INSERT INTO nw_categories (category_name, description) VALUES (%s, %s) ON CONFLICT DO NOTHING", ("Beverages", "Soft drinks, coffees, teas, beers, and ales"))
        cur.execute("INSERT INTO nw_categories (category_name, description) VALUES (%s, %s) ON CONFLICT DO NOTHING", ("Condiments", "Sweet and savory sauces, relishes, spreads, and seasonings"))
        cur.execute("INSERT INTO nw_categories (category_name, description) VALUES (%s, %s) ON CONFLICT DO NOTHING", ("Confections", "Desserts, candies, and sweet breads"))

        cur.execute("INSERT INTO nw_suppliers (company_name, contact_name, country, city) VALUES (%s, %s, %s, %s)", ("Exotic Liquids", "Charlotte Cooper", "UK", "London"))
        cur.execute("INSERT INTO nw_suppliers (company_name, contact_name, country, city) VALUES (%s, %s, %s, %s)", ("New Orleans Cajun Delights", "Shelley Burke", "USA", "New Orleans"))

        cur.execute("INSERT INTO nw_shippers (company_name, phone) VALUES (%s, %s)", ("Speedy Express", "(503) 555-9831"))
        cur.execute("INSERT INTO nw_shippers (company_name, phone) VALUES (%s, %s)", ("United Package", "(503) 555-3199"))

        cur.execute("INSERT INTO nw_employees (last_name, first_name, title, hire_date, country) VALUES (%s, %s, %s, %s, %s)", ("Davolio", "Nancy", "Sales Representative", "1992-05-01", "USA"))
        cur.execute("INSERT INTO nw_employees (last_name, first_name, title, hire_date, country) VALUES (%s, %s, %s, %s, %s)", ("Fuller", "Andrew", "Vice President, Sales", "1992-08-14", "USA"))

        cur.execute("INSERT INTO nw_customers (customer_id, company_name, contact_name, country, city) VALUES (%s, %s, %s, %s, %s)", ("ALFKI", "Alfreds Futterkiste", "Maria Anders", "Germany", "Berlin"))
        cur.execute("INSERT INTO nw_customers (customer_id, company_name, contact_name, country, city) VALUES (%s, %s, %s, %s, %s)", ("ANATR", "Ana Trujillo Emparedados", "Ana Trujillo", "Mexico", "Mexico D.F."))
        cur.execute("INSERT INTO nw_customers (customer_id, company_name, contact_name, country, city) VALUES (%s, %s, %s, %s, %s)", ("VINET", "Vins et alcools Chevalier", "Paul Henriot", "France", "Reims"))

        cur.execute("INSERT INTO nw_products (product_name, supplier_id, category_id, unit_price, units_in_stock) VALUES (%s, %s, %s, %s, %s)", ("Chai", 1, 1, 18.00, 39))
        cur.execute("INSERT INTO nw_products (product_name, supplier_id, category_id, unit_price, units_in_stock) VALUES (%s, %s, %s, %s, %s)", ("Chang", 1, 1, 19.00, 17))
        cur.execute("INSERT INTO nw_products (product_name, supplier_id, category_id, unit_price, units_in_stock) VALUES (%s, %s, %s, %s, %s)", ("Aniseed Syrup", 1, 2, 10.00, 13))

        cur.execute("INSERT INTO nw_orders (customer_id, employee_id, order_date, ship_via, freight, ship_country) VALUES (%s, %s, %s, %s, %s, %s)", ("VINET", 1, "1996-07-04", 1, 32.38, "France"))
        cur.execute("INSERT INTO nw_orders (customer_id, employee_id, order_date, ship_via, freight, ship_country) VALUES (%s, %s, %s, %s, %s, %s)", ("ALFKI", 2, "1997-08-25", 1, 29.46, "Germany"))
        cur.execute("INSERT INTO nw_orders (customer_id, employee_id, order_date, ship_via, freight, ship_country) VALUES (%s, %s, %s, %s, %s, %s)", ("ANATR", 1, "1996-09-18", 2, 11.61, "Mexico"))

        cur.execute("INSERT INTO nw_order_details (order_id, product_id, unit_price, quantity, discount) VALUES (%s, %s, %s, %s, %s)", (1, 1, 18.00, 12, 0.0))
        cur.execute("INSERT INTO nw_order_details (order_id, product_id, unit_price, quantity, discount) VALUES (%s, %s, %s, %s, %s)", (1, 2, 19.00, 10, 0.0))
        cur.execute("INSERT INTO nw_order_details (order_id, product_id, unit_price, quantity, discount) VALUES (%s, %s, %s, %s, %s)", (2, 3, 10.00, 5, 0.05))

    conn.commit()
    print("  Seeded northwind tables.")


def seed_nyc_taxi(conn: psycopg2.extensions.connection) -> None:
    with conn.cursor() as cur:
        cur.execute("TRUNCATE nyc_trips, nyc_taxi_zones, nyc_payment_types, nyc_rate_codes RESTART IDENTITY CASCADE")

        cur.execute("INSERT INTO nyc_payment_types (payment_type_id, payment_type_name, description) VALUES (%s, %s, %s)", (1, "Credit card", "Payment via credit or debit card"))
        cur.execute("INSERT INTO nyc_payment_types (payment_type_id, payment_type_name, description) VALUES (%s, %s, %s)", (2, "Cash", "Cash payment to driver"))
        cur.execute("INSERT INTO nyc_payment_types (payment_type_id, payment_type_name, description) VALUES (%s, %s, %s)", (3, "No charge", "Complimentary ride"))

        cur.execute("INSERT INTO nyc_rate_codes (rate_code_id, rate_code_name) VALUES (%s, %s)", (1, "Standard rate"))
        cur.execute("INSERT INTO nyc_rate_codes (rate_code_id, rate_code_name) VALUES (%s, %s)", (2, "JFK"))
        cur.execute("INSERT INTO nyc_rate_codes (rate_code_id, rate_code_name) VALUES (%s, %s)", (3, "Newark"))

        zones = [
            (1, "EWR", "Newark Airport", "EWR"),
            (132, "Queens", "JFK Airport", "Airports"),
            (161, "Manhattan", "Midtown Center", "Yellow Zone"),
            (236, "Manhattan", "Upper East Side South", "Yellow Zone"),
            (237, "Manhattan", "Upper East Side North", "Yellow Zone"),
        ]
        for z in zones:
            cur.execute("INSERT INTO nyc_taxi_zones (location_id, borough, zone, service_zone) VALUES (%s, %s, %s, %s)", z)

        trips = [
            ("2023-01-01 00:32:10", "2023-01-01 00:40:36", 1, 0.97, 161, 236, 1, 1, 9.30, 2.00, 14.30),
            ("2023-01-01 00:55:45", "2023-01-01 01:18:22", 2, 1.10, 236, 237, 1, 2, 7.90, 0.00, 12.90),
            ("2023-01-01 01:14:03", "2023-01-01 01:38:47", 1, 2.51, 161, 237, 1, 1, 14.80, 3.05, 20.85),
            ("2023-01-01 02:05:00", "2023-01-01 02:42:00", 1, 8.30, 161, 132, 2, 1, 52.00, 0.00, 56.50),
        ]
        for t in trips:
            cur.execute(
                """INSERT INTO nyc_trips
                (pickup_datetime, dropoff_datetime, passenger_count, trip_distance,
                 pickup_location_id, dropoff_location_id, rate_code_id, payment_type_id,
                 fare_amount, tip_amount, total_amount)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                t,
            )

    conn.commit()
    print("  Seeded nyc_taxi tables.")


def run() -> None:
    print("Connecting to database...")
    conn = psycopg2.connect(settings.database_url)
    try:
        print("Creating tables...")
        create_tables(conn)
        print("Seeding Northwind...")
        seed_northwind(conn)
        print("Seeding NYC Taxi...")
        seed_nyc_taxi(conn)
        print("Done. All seed data loaded.")
    finally:
        conn.close()


if __name__ == "__main__":
    run()
