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


def seed_tpch(conn: psycopg2.extensions.connection) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "TRUNCATE tpch_lineitem, tpch_partsupp, tpch_orders, tpch_part, "
            "tpch_supplier, tpch_customer, tpch_nation, tpch_region CASCADE"
        )

        # Standard TPC-H regions (always exactly 5)
        regions = [
            (0, "AFRICA"), (1, "AMERICA"), (2, "ASIA"),
            (3, "EUROPE"), (4, "MIDDLE EAST"),
        ]
        cur.executemany(
            "INSERT INTO tpch_region (r_regionkey, r_name) VALUES (%s, %s)",
            regions,
        )

        # Standard TPC-H nations (always exactly 25)
        nations = [
            (0, "ALGERIA", 0), (1, "ARGENTINA", 1), (2, "BRAZIL", 1),
            (3, "CANADA", 1), (4, "EGYPT", 4), (5, "ETHIOPIA", 0),
            (6, "FRANCE", 3), (7, "GERMANY", 3), (8, "INDIA", 2),
            (9, "INDONESIA", 2), (10, "IRAN", 4), (11, "IRAQ", 4),
            (12, "JAPAN", 2), (13, "JORDAN", 4), (14, "KENYA", 0),
            (15, "MOROCCO", 0), (16, "MOZAMBIQUE", 0), (17, "PERU", 1),
            (18, "CHINA", 2), (19, "ROMANIA", 3), (20, "SAUDI ARABIA", 4),
            (21, "VIETNAM", 2), (22, "RUSSIA", 3), (23, "UNITED KINGDOM", 3),
            (24, "UNITED STATES", 1),
        ]
        cur.executemany(
            "INSERT INTO tpch_nation (n_nationkey, n_name, n_regionkey) VALUES (%s, %s, %s)",
            nations,
        )

        # 10 suppliers across different nations
        suppliers = [
            (1, "Supplier#001", "N kD4on9OM Ipw3,gf0JBoQDd7tgrzrddZ", 17, "27-918-335-1736", 5755.94),
            (2, "Supplier#002", "89eJ5ksX3ImxJQBvxObC,", 5, "15-679-861-2259", 4032.68),
            (3, "Supplier#003", "q1,G3Pj6OjIuUYfUoH18BFTKP5e,YJZk6N", 1, "11-383-516-1199", 4192.40),
            (4, "Supplier#004", "Bk7ah4CK8SYQTepEmvMkkgMwg", 15, "25-843-787-7479", 1799.46),
            (5, "Supplier#005", "Gcdm2rJRzl5qlTVzc", 11, "21-151-690-3663", -283.84),
            (6, "Supplier#006", "tQxuVm7s7CnK",  0, "10-641-595-4627", 1365.46),
            (7, "Supplier#007", "s,4TicNGB4uO6PaSqNBUq", 23, "33-990-965-2201", 6820.35),
            (8, "Supplier#008", "9Sq4bBH2FQEmaFOocY45sRTxo6yuoG", 2, "12-931-665-5392", 6222.79),
            (9, "Supplier#009", "1KhUgZegwM3ua7dsYmekYBsK", 6, "16-580-316-4773", 1336.65),
            (10, "Supplier#010", "Saygah3gYWMp72i PY,cY3B",  7, "17-189-993-3739", 3822.68),
        ]
        cur.executemany(
            "INSERT INTO tpch_supplier (s_suppkey, s_name, s_address, s_nationkey, s_phone, s_acctbal) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            suppliers,
        )

        # 20 parts
        parts = [
            (1,  "goldenrod lavender spring chocolate lace",      "Manufacturer#1", "Brand#13", "PROMO BURNISHED COPPER",   7,  "JUMBO PKG",    901.00),
            (2,  "blush thistle blue yellow saddle",              "Manufacturer#1", "Brand#13", "LARGE BRUSHED BRASS",      1,  "LG CASE",      902.00),
            (3,  "dark green antique puff wheat",                 "Manufacturer#4", "Brand#42", "STANDARD POLISHED BRASS",  21, "WRAP CASE",    903.00),
            (4,  "floral forest brown coral peru",                "Manufacturer#3", "Brand#34", "SMALL PLATED BRASS",       14, "MED DRUM",     904.00),
            (5,  "forest blush chiffon thistle chocolate",        "Manufacturer#3", "Brand#32", "STANDARD POLISHED TIN",    15, "SM PKG",       905.00),
            (6,  "bisque cornsilk lawn forest magenta",           "Manufacturer#2", "Brand#24", "PROMO PLATED STEEL",       4,  "MED BAG",      906.00),
            (7,  "moccasin green puff thistle azure",             "Manufacturer#1", "Brand#11", "SMALL PLATED COPPER",      45, "SM BAG",       907.00),
            (8,  "misty lace wheat lemon gainsboro",              "Manufacturer#4", "Brand#44", "PROMO BURNISHED TIN",      41, "LG DRUM",      908.00),
            (9,  "thistle rose rosy tan linen",                   "Manufacturer#4", "Brand#43", "SMALL BURNISHED STEEL",    12, "WRAP CASE",    909.00),
            (10, "linen pink saddle puff powder",                 "Manufacturer#5", "Brand#54", "LARGE BURNISHED STEEL",    44, "LG CAN",       910.00),
            (11, "green tomato ghost violet slate",               "Manufacturer#2", "Brand#25", "STANDARD BURNISHED NICKEL",43, "WRAP BOX",     911.00),
            (12, "coral antique violet turquoise frosted",        "Manufacturer#3", "Brand#35", "MEDIUM ANODIZED STEEL",    25, "JUMBO CASE",   912.00),
            (13, "hot chartreuse blush green tan",                "Manufacturer#4", "Brand#45", "MEDIUM BURNISHED NICKEL",  40, "JUMBO PKG",    913.00),
            (14, "sandy cream puff steel aquamarine",             "Manufacturer#1", "Brand#13", "SMALL POLISHED STEEL",     28, "MED DRUM",     914.00),
            (15, "azure tomato bisque khaki cream",               "Manufacturer#5", "Brand#55", "LARGE ANODIZED BRASS",     45, "LG BOX",       915.00),
            (16, "purple chartreuse maroon linen tan",            "Manufacturer#1", "Brand#11", "PROMO PLATED TIN",         7,  "LG PKG",       916.00),
            (17, "wheat slate brown cream cyan",                  "Manufacturer#2", "Brand#23", "LARGE BRUSHED STEEL",      16, "MED CASE",     917.00),
            (18, "cream rose pink ghost papaya",                  "Manufacturer#3", "Brand#33", "SMALL ANODIZED STEEL",     10, "WRAP BOX",     918.00),
            (19, "peach cyan khaki rose aquamarine",              "Manufacturer#4", "Brand#42", "SMALL BURNISHED COPPER",   3,  "JUMBO BOX",    919.00),
            (20, "floral goldenrod spring maroon sandy",          "Manufacturer#5", "Brand#52", "LARGE POLISHED NICKEL",    31, "LG DRUM",      920.00),
        ]
        cur.executemany(
            "INSERT INTO tpch_part (p_partkey, p_name, p_mfgr, p_brand, p_type, p_size, p_container, p_retailprice) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            parts,
        )

        # Part-supplier combos (partsupp): 2 suppliers per part
        partsupp = [
            (1, 2, 3325, 771.64), (1, 5, 8076, 993.49),
            (2, 3, 8895, 337.09), (2, 7, 4969, 357.84),
            (3, 4, 4069, 357.84), (3, 8, 3110, 663.11),
            (4, 1, 1339, 2.87),   (4, 9, 6377, 205.73),
            (5, 2, 3552, 881.36), (5, 6, 3213, 5.35),
            (6, 3, 2355, 519.18), (6, 10, 9377, 150.21),
            (7, 4, 6581, 408.15), (7, 1, 1699, 116.65),
            (8, 5, 3288, 996.10), (8, 2, 4633, 551.66),
            (9, 6, 3712, 836.86), (9, 3, 8564, 957.55),
            (10, 7, 4219, 101.37),(10, 4, 9998, 357.16),
            (11, 8, 2669, 502.11),(12, 9, 6081, 205.61),
            (13,10, 3944, 601.56),(14, 1, 1603, 444.37),
            (15, 2, 1574, 390.93),(16, 3, 3829, 551.66),
            (17, 4, 9942, 357.84),(18, 5, 5023, 881.00),
            (19, 6, 2766, 663.11),(20, 7, 4402, 157.84),
        ]
        cur.executemany(
            "INSERT INTO tpch_partsupp (ps_partkey, ps_suppkey, ps_availqty, ps_supplycost) "
            "VALUES (%s, %s, %s, %s)",
            partsupp,
        )

        # 30 customers spread across nations
        customers = [
            (1,  "Customer#000000001", "IVhzIApeRb ot,c,E",          15, "25-989-741-2988", 711.56,  "BUILDING"),
            (2,  "Customer#000000002", "XSTf4,NCwDVaWNe6tEgvwfmRchLXak", 13, "23-768-687-3665", 121.65, "AUTOMOBILE"),
            (3,  "Customer#000000003", "MG9kdTD2WBHm",                 1,  "11-719-748-3364", 7498.12, "AUTOMOBILE"),
            (4,  "Customer#000000004", "XxVSJsLAGtn",                  4,  "14-128-190-5944", 2866.83, "MACHINERY"),
            (5,  "Customer#000000005", "KvpyuHCplrB84WgAiGV6sYpZq7Tj", 3,  "13-750-942-6364", 794.47,  "HOUSEHOLD"),
            (6,  "Customer#000000006", "sKZz0CsnMD7mp4Xd0YrBvx,LREYKUWAh", 20, "30-114-968-4951", 7638.57, "AUTOMOBILE"),
            (7,  "Customer#000000007", "TcGe5gaZNgVePxU5kRrvXBfkasDTea", 18, "28-190-982-9759", 9561.95, "AUTOMOBILE"),
            (8,  "Customer#000000008", "I0B10bB0AymmC, 0PrRYBCP1yGJ8xcBPmWhl5",  17, "27-147-574-9335", 6819.74, "BUILDING"),
            (9,  "Customer#000000009", "xKiAFTjUsCuxfeleNqefumTrjS",   8,  "18-338-906-3675", 8324.07, "FURNITURE"),
            (10, "Customer#000000010", "6LrEaV6KR6PLVcgl2ArL Q3rqzLzcT1 v2", 5, "15-741-346-9870", 2753.54, "HOUSEHOLD"),
            (11, "Customer#000000011", "PkWS 3HlXqwTuz34o",            23, "33-464-151-3439", -272.60, "BUILDING"),
            (12, "Customer#000000012", "9PWkPortal6oPECy0t21T",        13, "23-791-276-1263", 3396.49, "HOUSEHOLD"),
            (13, "Customer#000000013", "nsXQu0oVjD7PM659uC3SRSp",       3, "13-761-547-5974", 3857.34, "BUILDING"),
            (14, "Customer#000000014", "KXkletMlL2JQEA",               1,  "11-845-129-3851", 5266.30, "FURNITURE"),
            (15, "Customer#000000015", "YtWggXoOLdwdo7b0y,BZaGUQMLJMX1Y,EC,2T", 23, "33-687-542-7601", 2788.52, "HOUSEHOLD"),
            (16, "Customer#000000016", "cYiaeMLZSMAOQ2 d0W,",          10, "20-781-609-3107", 4681.03, "FURNITURE"),
            (17, "Customer#000000017", "izrh 6jdqtp2eqdtbkswDD9PAS",   2,  "12-970-682-3487", 6.34,    "AUTOMOBILE"),
            (18, "Customer#000000018", "3txGO AiuFux3zT0Z9NYacc",      6,  "16-155-215-1315", 5494.43, "BUILDING"),
            (19, "Customer#000000019", "uc,3bHIx84H,wdrmLOjVsiqXCq2tr", 18, "28-396-526-5053", 8914.71, "HOUSEHOLD"),
            (20, "Customer#000000020", "JrPk8Pqplj4Ne",                22, "32-957-234-8742", 7603.40, "FURNITURE"),
            (21, "Customer#000000021", "XYqVjg1L9nSuOweb",             8,  "18-902-614-8344", 1428.25, "MACHINERY"),
            (22, "Customer#000000022", "QI6p41,FNs5k7RZoCCVPUTkUdYpB",  3, "13-806-545-9701", 591.98,  "MACHINERY"),
            (23, "Customer#000000023", "OdY W13N7Be3OC5MpgfmcYss0Wn6TKT", 3, "13-312-472-8245", 3332.02, "HOUSEHOLD"),
            (24, "Customer#000000024", "HXy QJpgM3 tezmAi",            13, "23-127-851-8031", 9255.67, "MACHINERY"),
            (25, "Customer#000000025", "Hp8GyFQgGHFYSilH5tBfe",         0, "10-692-555-5602", 4983.51, "AUTOMOBILE"),
            (26, "Customer#000000026", "8ljrc5ZIOdiS",                  22, "32-363-455-4837", 5182.05, "AUTOMOBILE"),
            (27, "Customer#000000027", "To60H0oJnbhLhZTSoWq",          18, "28-190-442-1234", 9243.70, "BUILDING"),
            (28, "Customer#000000028", "iVyg0daQ,Tha8x2WPWA9m2529m",   24, "34-140-335-6976", 1007.18, "FURNITURE"),
            (29, "Customer#000000029", "sJ5adtfyAkCK63df2,vF25zyQMVYE34uh8", 0, "10-773-203-7342", 7618.27, "FURNITURE"),
            (30, "Customer#000000030", "nJDsELGAavU63Jl0c5NKsKfxqxQ09",  1, "11-764-165-5076", 9321.01, "BUILDING"),
        ]
        cur.executemany(
            "INSERT INTO tpch_customer "
            "(c_custkey, c_name, c_address, c_nationkey, c_phone, c_acctbal, c_mktsegment) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            customers,
        )

        # 75 orders spread across customers and dates
        import datetime as dt
        base = dt.date(1993, 1, 1)
        orders_data = [
            (1,  1,  'O', 173665.47, base + dt.timedelta(days=5),   '5-LOW',     'Clerk#000000951', 0),
            (2,  12, 'O', 46929.18,  base + dt.timedelta(days=10),  '1-URGENT',  'Clerk#000000880', 0),
            (3,  2,  'F', 193846.25, base + dt.timedelta(days=15),  '5-LOW',     'Clerk#000000955', 0),
            (4,  14, 'O', 32151.78,  base + dt.timedelta(days=20),  '5-LOW',     'Clerk#000000124', 0),
            (5,  5,  'F', 144659.20, base + dt.timedelta(days=25),  '5-LOW',     'Clerk#000000925', 0),
            (6,  22, 'F', 58749.59,  base + dt.timedelta(days=30),  '4-NOT SPECIFIED', 'Clerk#000000106', 0),
            (7,  8,  'O', 252004.18, base + dt.timedelta(days=35),  '2-HIGH',    'Clerk#000000440', 0),
            (8,  17, 'O', 229909.29, base + dt.timedelta(days=40),  '1-URGENT',  'Clerk#000000731', 0),
            (9,  29, 'F', 182775.04, base + dt.timedelta(days=45),  '3-MEDIUM',  'Clerk#000000354', 0),
            (10, 16, 'F', 65522.20,  base + dt.timedelta(days=50),  '5-LOW',     'Clerk#000000460', 0),
            (11, 21, 'O', 282244.15, base + dt.timedelta(days=55),  '1-URGENT',  'Clerk#000000881', 0),
            (12, 3,  'F', 215829.75, base + dt.timedelta(days=60),  '2-HIGH',    'Clerk#000000124', 0),
            (13, 7,  'F', 188124.55, base + dt.timedelta(days=65),  '3-MEDIUM',  'Clerk#000000141', 0),
            (14, 20, 'O', 117975.96, base + dt.timedelta(days=70),  '5-LOW',     'Clerk#000000625', 0),
            (15, 11, 'F', 297065.83, base + dt.timedelta(days=75),  '2-HIGH',    'Clerk#000000026', 0),
            (16, 4,  'O', 226058.44, base + dt.timedelta(days=80),  '2-HIGH',    'Clerk#000000616', 0),
            (17, 15, 'F', 138817.63, base + dt.timedelta(days=85),  '5-LOW',     'Clerk#000000483', 0),
            (18, 25, 'O', 301705.53, base + dt.timedelta(days=90),  '4-NOT SPECIFIED', 'Clerk#000000440', 0),
            (19, 9,  'F', 96000.45,  base + dt.timedelta(days=95),  '3-MEDIUM',  'Clerk#000000313', 0),
            (20, 30, 'O', 188244.55, base + dt.timedelta(days=100), '1-URGENT',  'Clerk#000000355', 0),
            (21, 6,  'O', 342180.50, base + dt.timedelta(days=105), '1-URGENT',  'Clerk#000000618', 0),
            (22, 19, 'F', 71368.09,  base + dt.timedelta(days=110), '5-LOW',     'Clerk#000000300', 0),
            (23, 27, 'O', 254364.61, base + dt.timedelta(days=115), '3-MEDIUM',  'Clerk#000000330', 0),
            (24, 10, 'F', 87819.54,  base + dt.timedelta(days=120), '4-NOT SPECIFIED', 'Clerk#000000655', 0),
            (25, 13, 'O', 178002.94, base + dt.timedelta(days=125), '2-HIGH',    'Clerk#000000919', 0),
            (26, 24, 'F', 93986.19,  base + dt.timedelta(days=130), '5-LOW',     'Clerk#000000541', 0),
            (27, 18, 'O', 212103.38, base + dt.timedelta(days=135), '3-MEDIUM',  'Clerk#000000501', 0),
            (28, 23, 'F', 105933.89, base + dt.timedelta(days=140), '4-NOT SPECIFIED', 'Clerk#000000440', 0),
            (29, 26, 'O', 166261.09, base + dt.timedelta(days=145), '2-HIGH',    'Clerk#000000601', 0),
            (30, 28, 'F', 58401.09,  base + dt.timedelta(days=150), '5-LOW',     'Clerk#000000038', 0),
            (31, 2,  'O', 227096.08, base + dt.timedelta(days=155), '3-MEDIUM',  'Clerk#000000292', 0),
            (32, 7,  'O', 300838.99, base + dt.timedelta(days=160), '2-HIGH',    'Clerk#000000786', 0),
            (33, 12, 'F', 196278.64, base + dt.timedelta(days=165), '4-NOT SPECIFIED', 'Clerk#000000440', 0),
            (34, 17, 'O', 88454.88,  base + dt.timedelta(days=170), '1-URGENT',  'Clerk#000000731', 0),
            (35, 22, 'F', 127207.96, base + dt.timedelta(days=175), '5-LOW',     'Clerk#000000480', 0),
            (36, 3,  'O', 212847.49, base + dt.timedelta(days=180), '2-HIGH',    'Clerk#000000330', 0),
            (37, 8,  'F', 156295.55, base + dt.timedelta(days=185), '3-MEDIUM',  'Clerk#000000430', 0),
            (38, 14, 'O', 287018.44, base + dt.timedelta(days=190), '1-URGENT',  'Clerk#000000811', 0),
            (39, 19, 'F', 74897.03,  base + dt.timedelta(days=195), '5-LOW',     'Clerk#000000131', 0),
            (40, 24, 'O', 164530.68, base + dt.timedelta(days=200), '4-NOT SPECIFIED', 'Clerk#000000220', 0),
            (41, 1,  'O', 238019.22, base + dt.timedelta(days=205), '2-HIGH',    'Clerk#000000355', 0),
            (42, 5,  'F', 121078.35, base + dt.timedelta(days=210), '3-MEDIUM',  'Clerk#000000001', 0),
            (43, 10, 'O', 193942.77, base + dt.timedelta(days=215), '1-URGENT',  'Clerk#000000440', 0),
            (44, 15, 'F', 85131.14,  base + dt.timedelta(days=220), '5-LOW',     'Clerk#000000131', 0),
            (45, 20, 'O', 311666.12, base + dt.timedelta(days=225), '4-NOT SPECIFIED', 'Clerk#000000380', 0),
            (46, 25, 'F', 99671.23,  base + dt.timedelta(days=230), '2-HIGH',    'Clerk#000000490', 0),
            (47, 30, 'O', 176707.00, base + dt.timedelta(days=235), '3-MEDIUM',  'Clerk#000000370', 0),
            (48, 6,  'F', 220441.12, base + dt.timedelta(days=240), '1-URGENT',  'Clerk#000000618', 0),
            (49, 11, 'O', 143561.12, base + dt.timedelta(days=245), '5-LOW',     'Clerk#000000320', 0),
            (50, 16, 'F', 258831.42, base + dt.timedelta(days=250), '2-HIGH',    'Clerk#000000790', 0),
            (51, 21, 'O', 95119.08,  base + dt.timedelta(days=255), '3-MEDIUM',  'Clerk#000000640', 0),
            (52, 26, 'F', 207638.68, base + dt.timedelta(days=260), '4-NOT SPECIFIED', 'Clerk#000000770', 0),
            (53, 4,  'O', 169031.87, base + dt.timedelta(days=265), '1-URGENT',  'Clerk#000000001', 0),
            (54, 9,  'F', 113278.46, base + dt.timedelta(days=270), '5-LOW',     'Clerk#000000330', 0),
            (55, 14, 'O', 289085.35, base + dt.timedelta(days=275), '2-HIGH',    'Clerk#000000350', 0),
            (56, 19, 'F', 78614.21,  base + dt.timedelta(days=280), '3-MEDIUM',  'Clerk#000000140', 0),
            (57, 24, 'O', 201344.11, base + dt.timedelta(days=285), '5-LOW',     'Clerk#000000210', 0),
            (58, 29, 'F', 143210.30, base + dt.timedelta(days=290), '1-URGENT',  'Clerk#000000920', 0),
            (59, 2,  'O', 314422.85, base + dt.timedelta(days=295), '2-HIGH',    'Clerk#000000640', 0),
            (60, 7,  'F', 189144.48, base + dt.timedelta(days=300), '4-NOT SPECIFIED', 'Clerk#000000001', 0),
            (61, 12, 'O', 107836.40, base + dt.timedelta(days=305), '3-MEDIUM',  'Clerk#000000810', 0),
            (62, 17, 'F', 227819.24, base + dt.timedelta(days=310), '5-LOW',     'Clerk#000000170', 0),
            (63, 22, 'O', 77274.41,  base + dt.timedelta(days=315), '1-URGENT',  'Clerk#000000220', 0),
            (64, 27, 'F', 162009.06, base + dt.timedelta(days=320), '2-HIGH',    'Clerk#000000430', 0),
            (65, 3,  'O', 99812.44,  base + dt.timedelta(days=325), '3-MEDIUM',  'Clerk#000000440', 0),
            (66, 8,  'F', 275474.23, base + dt.timedelta(days=330), '4-NOT SPECIFIED', 'Clerk#000000600', 0),
            (67, 13, 'O', 218503.30, base + dt.timedelta(days=335), '1-URGENT',  'Clerk#000000440', 0),
            (68, 18, 'F', 135236.59, base + dt.timedelta(days=340), '5-LOW',     'Clerk#000000790', 0),
            (69, 23, 'O', 291055.04, base + dt.timedelta(days=345), '2-HIGH',    'Clerk#000000870', 0),
            (70, 28, 'F', 63921.14,  base + dt.timedelta(days=350), '3-MEDIUM',  'Clerk#000000330', 0),
            (71, 6,  'O', 198372.64, base + dt.timedelta(days=355), '5-LOW',     'Clerk#000000001', 0),
            (72, 11, 'F', 149102.56, base + dt.timedelta(days=360), '1-URGENT',  'Clerk#000000001', 0),
            (73, 16, 'O', 233004.02, base + dt.timedelta(days=365), '2-HIGH',    'Clerk#000000380', 0),
            (74, 21, 'F', 185834.00, base + dt.timedelta(days=370), '4-NOT SPECIFIED', 'Clerk#000000220', 0),
            (75, 26, 'O', 102419.73, base + dt.timedelta(days=375), '3-MEDIUM',  'Clerk#000000710', 0),
        ]
        cur.executemany(
            "INSERT INTO tpch_orders "
            "(o_orderkey, o_custkey, o_orderstatus, o_totalprice, o_orderdate, "
            "o_orderpriority, o_clerk, o_shippriority) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            orders_data,
        )

        # 150 line items (2 per order)
        import datetime as dt
        lineitems = []
        part_supp_pairs = [(1,2),(1,5),(2,3),(2,7),(3,4),(3,8),(4,1),(4,9),(5,2),(5,6),
                           (6,3),(6,10),(7,4),(7,1),(8,5),(8,2),(9,6),(9,3),(10,7),(10,4),
                           (11,8),(12,9),(13,10),(14,1),(15,2),(16,3),(17,4),(18,5),(19,6),(20,7)]
        for i, (okey, custkey, *_) in enumerate(orders_data):
            ps1 = part_supp_pairs[i % len(part_supp_pairs)]
            ps2 = part_supp_pairs[(i + 1) % len(part_supp_pairs)]
            ship1 = base + dt.timedelta(days=5 * i + 7)
            ship2 = base + dt.timedelta(days=5 * i + 14)
            lineitems.append((okey, ps1[0], ps1[1], 1, 17.00, 17476.87, 0.04, 0.02, 'N', 'O', ship1, ship1 + dt.timedelta(days=3), ship1 + dt.timedelta(days=5), 'DELIVER IN PERSON', 'TRUCK', 'line 1'))
            lineitems.append((okey, ps2[0], ps2[1], 2, 36.00, 34850.16, 0.09, 0.06, 'R', 'F', ship2, ship2 + dt.timedelta(days=3), ship2 + dt.timedelta(days=5), 'NONE', 'MAIL',  'line 2'))

        cur.executemany(
            "INSERT INTO tpch_lineitem "
            "(l_orderkey, l_partkey, l_suppkey, l_linenumber, l_quantity, l_extendedprice, "
            "l_discount, l_tax, l_returnflag, l_linestatus, l_shipdate, l_commitdate, "
            "l_receiptdate, l_shipinstruct, l_shipmode, l_comment) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            lineitems,
        )

    conn.commit()
    print("  Seeded tpch tables.")


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
        print("Seeding TPC-H...")
        seed_tpch(conn)
        print("Seeding NYC Taxi...")
        seed_nyc_taxi(conn)
        print("Done. All seed data loaded.")
    finally:
        conn.close()


if __name__ == "__main__":
    run()
