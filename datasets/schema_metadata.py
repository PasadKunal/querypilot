"""
Central metadata registry for all demo schemas.

Each database entry contains table descriptions, column-level metadata
(type, description, sample values), and foreign key relationships.
The embedder reads this file to produce every pgvector embedding record.
"""

SCHEMA_METADATA: dict = {
    "northwind": {
        "description": "Classic trading company database tracking customers, orders, products, employees, and suppliers.",
        "tables": {
            "nw_categories": {
                "description": "Product categories used to group products in the catalog.",
                "columns": {
                    "category_id": {
                        "type": "INTEGER",
                        "description": "Unique identifier for the category.",
                        "sample_values": [1, 2, 3, 4, 5],
                    },
                    "category_name": {
                        "type": "VARCHAR",
                        "description": "Name of the product category.",
                        "sample_values": ["Beverages", "Condiments", "Confections", "Dairy Products", "Grains/Cereals"],
                    },
                    "description": {
                        "type": "TEXT",
                        "description": "Full description of what products belong in this category.",
                        "sample_values": ["Soft drinks, coffees, teas, beers, and ales", "Sweet and savory sauces, relishes, spreads, and seasonings"],
                    },
                },
            },
            "nw_suppliers": {
                "description": "Companies that supply products to Northwind.",
                "columns": {
                    "supplier_id": {
                        "type": "INTEGER",
                        "description": "Unique identifier for the supplier.",
                        "sample_values": [1, 2, 3, 4, 5],
                    },
                    "company_name": {
                        "type": "VARCHAR",
                        "description": "Name of the supplier company.",
                        "sample_values": ["Exotic Liquids", "New Orleans Cajun Delights", "Grandma Kelly's Homestead"],
                    },
                    "country": {
                        "type": "VARCHAR",
                        "description": "Country where the supplier is located.",
                        "sample_values": ["UK", "USA", "Japan", "Germany", "Australia"],
                    },
                    "city": {
                        "type": "VARCHAR",
                        "description": "City where the supplier is based.",
                        "sample_values": ["London", "New Orleans", "Ann Arbor", "Tokyo", "Sydney"],
                    },
                },
            },
            "nw_shippers": {
                "description": "Shipping companies used to deliver orders.",
                "columns": {
                    "shipper_id": {
                        "type": "INTEGER",
                        "description": "Unique identifier for the shipper.",
                        "sample_values": [1, 2, 3],
                    },
                    "company_name": {
                        "type": "VARCHAR",
                        "description": "Name of the shipping company.",
                        "sample_values": ["Speedy Express", "United Package", "Federal Shipping"],
                    },
                    "phone": {
                        "type": "VARCHAR",
                        "description": "Shipper contact phone number.",
                        "sample_values": ["(503) 555-9831", "(503) 555-3199", "(503) 555-9931"],
                    },
                },
            },
            "nw_employees": {
                "description": "Northwind employees who manage and process orders.",
                "columns": {
                    "employee_id": {
                        "type": "INTEGER",
                        "description": "Unique identifier for the employee.",
                        "sample_values": [1, 2, 3, 4, 5],
                    },
                    "last_name": {
                        "type": "VARCHAR",
                        "description": "Employee's last name.",
                        "sample_values": ["Davolio", "Fuller", "Leverling", "Peacock", "Buchanan"],
                    },
                    "first_name": {
                        "type": "VARCHAR",
                        "description": "Employee's first name.",
                        "sample_values": ["Nancy", "Andrew", "Janet", "Margaret", "Steven"],
                    },
                    "title": {
                        "type": "VARCHAR",
                        "description": "Job title of the employee.",
                        "sample_values": ["Sales Representative", "Vice President, Sales", "Sales Manager", "Inside Sales Coordinator"],
                    },
                    "hire_date": {
                        "type": "DATE",
                        "description": "Date the employee was hired.",
                        "sample_values": ["1992-05-01", "1992-08-14", "1993-04-01"],
                    },
                    "country": {
                        "type": "VARCHAR",
                        "description": "Country where the employee is based.",
                        "sample_values": ["USA", "UK"],
                    },
                    "reports_to": {
                        "type": "INTEGER",
                        "description": "Employee ID of this employee's manager (self-referencing FK).",
                        "sample_values": [2, 2, 2, 2, 2],
                    },
                },
            },
            "nw_customers": {
                "description": "Companies and individuals that purchase products from Northwind.",
                "columns": {
                    "customer_id": {
                        "type": "VARCHAR(5)",
                        "description": "Unique 5-character customer code.",
                        "sample_values": ["ALFKI", "ANATR", "ANTON", "AROUT", "BERGS"],
                    },
                    "company_name": {
                        "type": "VARCHAR",
                        "description": "Name of the customer company.",
                        "sample_values": ["Alfreds Futterkiste", "Ana Trujillo Emparedados", "Antonio Moreno Taquería", "Around the Horn"],
                    },
                    "contact_name": {
                        "type": "VARCHAR",
                        "description": "Name of the primary contact at the customer company.",
                        "sample_values": ["Maria Anders", "Ana Trujillo", "Antonio Moreno", "Thomas Hardy"],
                    },
                    "country": {
                        "type": "VARCHAR",
                        "description": "Country where the customer is located.",
                        "sample_values": ["Germany", "Mexico", "USA", "UK", "France", "Brazil"],
                    },
                    "city": {
                        "type": "VARCHAR",
                        "description": "City where the customer is based.",
                        "sample_values": ["Berlin", "México D.F.", "London", "Madrid", "Paris"],
                    },
                },
            },
            "nw_products": {
                "description": "Products available for purchase in the Northwind catalog.",
                "columns": {
                    "product_id": {
                        "type": "INTEGER",
                        "description": "Unique identifier for the product.",
                        "sample_values": [1, 2, 3, 4, 5],
                    },
                    "product_name": {
                        "type": "VARCHAR",
                        "description": "Name of the product.",
                        "sample_values": ["Chai", "Chang", "Aniseed Syrup", "Chef Anton's Cajun Seasoning", "Ikura"],
                    },
                    "supplier_id": {
                        "type": "INTEGER",
                        "description": "ID of the supplier who provides this product. References nw_suppliers.",
                        "sample_values": [1, 1, 1, 2, 4],
                    },
                    "category_id": {
                        "type": "INTEGER",
                        "description": "ID of the category this product belongs to. References nw_categories.",
                        "sample_values": [1, 1, 2, 2, 8],
                    },
                    "unit_price": {
                        "type": "NUMERIC",
                        "description": "List price per unit of this product.",
                        "sample_values": [18.00, 19.00, 10.00, 22.00, 31.00],
                    },
                    "units_in_stock": {
                        "type": "SMALLINT",
                        "description": "Number of units currently in stock.",
                        "sample_values": [39, 17, 13, 53, 31],
                    },
                    "discontinued": {
                        "type": "BOOLEAN",
                        "description": "Whether the product has been discontinued and is no longer sold.",
                        "sample_values": [False, False, False, True],
                    },
                },
            },
            "nw_orders": {
                "description": "Customer orders placed with Northwind, including shipping and date information.",
                "columns": {
                    "order_id": {
                        "type": "INTEGER",
                        "description": "Unique identifier for the order.",
                        "sample_values": [10248, 10249, 10250, 10251, 10252],
                    },
                    "customer_id": {
                        "type": "VARCHAR(5)",
                        "description": "ID of the customer who placed the order. References nw_customers.",
                        "sample_values": ["VINET", "TOMSP", "HANAR", "VICTE", "SUPRD"],
                    },
                    "employee_id": {
                        "type": "INTEGER",
                        "description": "ID of the employee who processed the order. References nw_employees.",
                        "sample_values": [5, 6, 4, 3, 4],
                    },
                    "order_date": {
                        "type": "DATE",
                        "description": "Date when the order was placed.",
                        "sample_values": ["1996-07-04", "1996-07-05", "1996-07-08"],
                    },
                    "shipped_date": {
                        "type": "DATE",
                        "description": "Date when the order was shipped to the customer.",
                        "sample_values": ["1996-07-16", "1996-07-10", "1996-07-12"],
                    },
                    "ship_via": {
                        "type": "INTEGER",
                        "description": "ID of the shipping company used. References nw_shippers.",
                        "sample_values": [3, 1, 2, 1, 2],
                    },
                    "freight": {
                        "type": "NUMERIC",
                        "description": "Shipping cost charged for the order.",
                        "sample_values": [32.38, 11.61, 65.83, 41.34, 51.30],
                    },
                    "ship_country": {
                        "type": "VARCHAR",
                        "description": "Country the order was shipped to.",
                        "sample_values": ["France", "Germany", "Brazil", "Belgium", "Switzerland"],
                    },
                },
            },
            "nw_order_details": {
                "description": "Line items for each order, linking orders to products with quantity and price.",
                "columns": {
                    "order_id": {
                        "type": "INTEGER",
                        "description": "Order this line item belongs to. References nw_orders.",
                        "sample_values": [10248, 10248, 10248, 10249, 10249],
                    },
                    "product_id": {
                        "type": "INTEGER",
                        "description": "Product on this line item. References nw_products.",
                        "sample_values": [11, 42, 72, 14, 51],
                    },
                    "unit_price": {
                        "type": "NUMERIC",
                        "description": "Price per unit at the time the order was placed (may differ from current list price).",
                        "sample_values": [14.00, 9.80, 34.80, 18.60, 42.40],
                    },
                    "quantity": {
                        "type": "SMALLINT",
                        "description": "Number of units ordered.",
                        "sample_values": [12, 10, 5, 9, 40],
                    },
                    "discount": {
                        "type": "REAL",
                        "description": "Discount percentage applied to the line item (0.0 to 1.0).",
                        "sample_values": [0.0, 0.0, 0.0, 0.05, 0.05],
                    },
                },
            },
        },
        "foreign_keys": [
            {"from_table": "nw_products", "from_column": "supplier_id", "to_table": "nw_suppliers", "to_column": "supplier_id"},
            {"from_table": "nw_products", "from_column": "category_id", "to_table": "nw_categories", "to_column": "category_id"},
            {"from_table": "nw_orders", "from_column": "customer_id", "to_table": "nw_customers", "to_column": "customer_id"},
            {"from_table": "nw_orders", "from_column": "employee_id", "to_table": "nw_employees", "to_column": "employee_id"},
            {"from_table": "nw_orders", "from_column": "ship_via", "to_table": "nw_shippers", "to_column": "shipper_id"},
            {"from_table": "nw_order_details", "from_column": "order_id", "to_table": "nw_orders", "to_column": "order_id"},
            {"from_table": "nw_order_details", "from_column": "product_id", "to_table": "nw_products", "to_column": "product_id"},
            {"from_table": "nw_employees", "from_column": "reports_to", "to_table": "nw_employees", "to_column": "employee_id"},
        ],
    },

    "tpch": {
        "description": "TPC-H analytical benchmark database covering orders, line items, customers, suppliers, parts, and geography.",
        "tables": {
            "tpch_region": {
                "description": "Geographic regions of the world (e.g., AFRICA, AMERICA, ASIA).",
                "columns": {
                    "r_regionkey": {
                        "type": "INTEGER",
                        "description": "Unique identifier for the region.",
                        "sample_values": [0, 1, 2, 3, 4],
                    },
                    "r_name": {
                        "type": "VARCHAR",
                        "description": "Name of the geographic region.",
                        "sample_values": ["AFRICA", "AMERICA", "ASIA", "EUROPE", "MIDDLE EAST"],
                    },
                },
            },
            "tpch_nation": {
                "description": "Countries/nations, each belonging to a geographic region.",
                "columns": {
                    "n_nationkey": {
                        "type": "INTEGER",
                        "description": "Unique identifier for the nation.",
                        "sample_values": [0, 1, 2, 3, 4],
                    },
                    "n_name": {
                        "type": "VARCHAR",
                        "description": "Name of the nation.",
                        "sample_values": ["ALGERIA", "ARGENTINA", "BRAZIL", "CANADA", "EGYPT"],
                    },
                    "n_regionkey": {
                        "type": "INTEGER",
                        "description": "Region this nation belongs to. References tpch_region.",
                        "sample_values": [0, 1, 1, 1, 4],
                    },
                },
            },
            "tpch_customer": {
                "description": "Customers who place orders in the TPC-H benchmark.",
                "columns": {
                    "c_custkey": {
                        "type": "INTEGER",
                        "description": "Unique customer identifier.",
                        "sample_values": [1, 2, 3, 4, 5],
                    },
                    "c_name": {
                        "type": "VARCHAR",
                        "description": "Customer name.",
                        "sample_values": ["Customer#000000001", "Customer#000000002", "Customer#000000003"],
                    },
                    "c_nationkey": {
                        "type": "INTEGER",
                        "description": "Nation this customer belongs to. References tpch_nation.",
                        "sample_values": [15, 13, 1, 4, 3],
                    },
                    "c_acctbal": {
                        "type": "NUMERIC",
                        "description": "Customer account balance.",
                        "sample_values": [711.56, 121.65, 7498.12, 2866.83, 794.47],
                    },
                    "c_mktsegment": {
                        "type": "VARCHAR",
                        "description": "Market segment the customer belongs to.",
                        "sample_values": ["BUILDING", "AUTOMOBILE", "MACHINERY", "FURNITURE", "HOUSEHOLD"],
                    },
                },
            },
            "tpch_supplier": {
                "description": "Suppliers who provide parts used in orders.",
                "columns": {
                    "s_suppkey": {
                        "type": "INTEGER",
                        "description": "Unique supplier identifier.",
                        "sample_values": [1, 2, 3, 4, 5],
                    },
                    "s_name": {
                        "type": "VARCHAR",
                        "description": "Supplier name.",
                        "sample_values": ["Supplier#000000001", "Supplier#000000002", "Supplier#000000003"],
                    },
                    "s_nationkey": {
                        "type": "INTEGER",
                        "description": "Nation this supplier is based in. References tpch_nation.",
                        "sample_values": [17, 0, 1, 4, 3],
                    },
                    "s_acctbal": {
                        "type": "NUMERIC",
                        "description": "Supplier account balance.",
                        "sample_values": [5755.94, 4032.68, 4192.40, 7627.85, 5989.02],
                    },
                },
            },
            "tpch_part": {
                "description": "Parts that can be ordered and supplied.",
                "columns": {
                    "p_partkey": {
                        "type": "INTEGER",
                        "description": "Unique part identifier.",
                        "sample_values": [1, 2, 3, 4, 5],
                    },
                    "p_name": {
                        "type": "VARCHAR",
                        "description": "Descriptive name of the part.",
                        "sample_values": ["goldenrod lavender spring chocolate lace", "blush thistle blue yellow saddle"],
                    },
                    "p_brand": {
                        "type": "VARCHAR",
                        "description": "Brand of the part.",
                        "sample_values": ["Brand#13", "Brand#11", "Brand#14", "Brand#43", "Brand#34"],
                    },
                    "p_type": {
                        "type": "VARCHAR",
                        "description": "Type/category of the part.",
                        "sample_values": ["PROMO ANODIZED STEEL", "LARGE BURNISHED NICKEL", "STANDARD POLISHED BRASS"],
                    },
                    "p_retailprice": {
                        "type": "NUMERIC",
                        "description": "Retail price of the part.",
                        "sample_values": [901.00, 902.00, 903.00, 904.00, 905.00],
                    },
                },
            },
            "tpch_partsupp": {
                "description": "Which suppliers can provide which parts, and at what cost and quantity.",
                "columns": {
                    "ps_partkey": {
                        "type": "INTEGER",
                        "description": "Part key. References tpch_part.",
                        "sample_values": [1, 1, 1, 1, 2],
                    },
                    "ps_suppkey": {
                        "type": "INTEGER",
                        "description": "Supplier key. References tpch_supplier.",
                        "sample_values": [2, 2502, 5002, 7502, 3],
                    },
                    "ps_availqty": {
                        "type": "INTEGER",
                        "description": "Quantity of this part currently available from this supplier.",
                        "sample_values": [3325, 8076, 3956, 4069, 8895],
                    },
                    "ps_supplycost": {
                        "type": "NUMERIC",
                        "description": "Cost to acquire one unit of this part from this supplier.",
                        "sample_values": [771.64, 993.49, 337.09, 357.84, 80.37],
                    },
                },
            },
            "tpch_orders": {
                "description": "Customer orders in the TPC-H benchmark.",
                "columns": {
                    "o_orderkey": {
                        "type": "INTEGER",
                        "description": "Unique order identifier.",
                        "sample_values": [1, 2, 3, 4, 5],
                    },
                    "o_custkey": {
                        "type": "INTEGER",
                        "description": "Customer who placed this order. References tpch_customer.",
                        "sample_values": [370, 781, 1234, 1369, 445],
                    },
                    "o_orderstatus": {
                        "type": "CHAR(1)",
                        "description": "Status of the order: O (open), F (fulfilled), P (partially fulfilled).",
                        "sample_values": ["O", "F", "P"],
                    },
                    "o_totalprice": {
                        "type": "NUMERIC",
                        "description": "Total dollar value of the order.",
                        "sample_values": [173665.47, 46929.18, 193846.25, 32151.78, 144659.20],
                    },
                    "o_orderdate": {
                        "type": "DATE",
                        "description": "Date the order was placed.",
                        "sample_values": ["1996-01-02", "1996-12-01", "1993-10-14"],
                    },
                    "o_orderpriority": {
                        "type": "VARCHAR",
                        "description": "Priority level of the order.",
                        "sample_values": ["5-LOW", "1-URGENT", "2-HIGH", "3-MEDIUM", "4-NOT SPECIFIED"],
                    },
                },
            },
            "tpch_lineitem": {
                "description": "Individual line items within orders, each representing one part from one supplier.",
                "columns": {
                    "l_orderkey": {
                        "type": "INTEGER",
                        "description": "Order this line item belongs to. References tpch_orders.",
                        "sample_values": [1, 1, 1, 1, 2],
                    },
                    "l_partkey": {
                        "type": "INTEGER",
                        "description": "Part on this line item. References tpch_part.",
                        "sample_values": [155190, 67310, 63700, 2132, 106170],
                    },
                    "l_suppkey": {
                        "type": "INTEGER",
                        "description": "Supplier providing the part. References tpch_supplier.",
                        "sample_values": [7706, 7311, 3701, 4633, 1191],
                    },
                    "l_quantity": {
                        "type": "NUMERIC",
                        "description": "Quantity of the part ordered on this line item.",
                        "sample_values": [17.00, 36.00, 8.00, 28.00, 24.00],
                    },
                    "l_extendedprice": {
                        "type": "NUMERIC",
                        "description": "Total price for this line item before discount (quantity x part price).",
                        "sample_values": [21168.23, 45983.16, 13309.60, 28955.64, 22824.48],
                    },
                    "l_discount": {
                        "type": "NUMERIC",
                        "description": "Discount fraction applied to this line item (0.00 to 0.10).",
                        "sample_values": [0.04, 0.09, 0.10, 0.09, 0.10],
                    },
                    "l_returnflag": {
                        "type": "CHAR(1)",
                        "description": "Whether the item was returned: R (returned), A (accepted), N (not yet returned).",
                        "sample_values": ["N", "R", "A"],
                    },
                    "l_shipdate": {
                        "type": "DATE",
                        "description": "Date this line item was shipped.",
                        "sample_values": ["1996-03-13", "1996-04-12", "1994-01-29"],
                    },
                    "l_shipmode": {
                        "type": "VARCHAR",
                        "description": "Shipping mode used for this line item.",
                        "sample_values": ["TRUCK", "MAIL", "REG AIR", "AIR", "FOB", "SHIP", "RAIL"],
                    },
                },
            },
        },
        "foreign_keys": [
            {"from_table": "tpch_nation", "from_column": "n_regionkey", "to_table": "tpch_region", "to_column": "r_regionkey"},
            {"from_table": "tpch_customer", "from_column": "c_nationkey", "to_table": "tpch_nation", "to_column": "n_nationkey"},
            {"from_table": "tpch_supplier", "from_column": "s_nationkey", "to_table": "tpch_nation", "to_column": "n_nationkey"},
            {"from_table": "tpch_partsupp", "from_column": "ps_partkey", "to_table": "tpch_part", "to_column": "p_partkey"},
            {"from_table": "tpch_partsupp", "from_column": "ps_suppkey", "to_table": "tpch_supplier", "to_column": "s_suppkey"},
            {"from_table": "tpch_orders", "from_column": "o_custkey", "to_table": "tpch_customer", "to_column": "c_custkey"},
            {"from_table": "tpch_lineitem", "from_column": "l_orderkey", "to_table": "tpch_orders", "to_column": "o_orderkey"},
        ],
    },

    "nyc_taxi": {
        "description": "NYC TLC taxi trip data for time-series, geospatial aggregation, and revenue analysis queries.",
        "tables": {
            "nyc_taxi_zones": {
                "description": "Geographic pickup and dropoff zones across New York City boroughs.",
                "columns": {
                    "location_id": {
                        "type": "INTEGER",
                        "description": "Unique zone identifier used in trip records.",
                        "sample_values": [1, 2, 3, 4, 132],
                    },
                    "borough": {
                        "type": "VARCHAR",
                        "description": "NYC borough the zone belongs to.",
                        "sample_values": ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island", "EWR"],
                    },
                    "zone": {
                        "type": "VARCHAR",
                        "description": "Descriptive name of the pickup or dropoff zone.",
                        "sample_values": ["Newark Airport", "Jamaica Bay", "Allerton/Pelham Gardens", "JFK Airport", "Times Sq/Theatre District"],
                    },
                    "service_zone": {
                        "type": "VARCHAR",
                        "description": "Broader service area classification for the zone.",
                        "sample_values": ["EWR", "Boro Zone", "Yellow Zone", "Airports"],
                    },
                },
            },
            "nyc_payment_types": {
                "description": "Payment method options available for taxi trips.",
                "columns": {
                    "payment_type_id": {
                        "type": "INTEGER",
                        "description": "Numeric code for the payment type.",
                        "sample_values": [1, 2, 3, 4, 5, 6],
                    },
                    "payment_type_name": {
                        "type": "VARCHAR",
                        "description": "Name of the payment method.",
                        "sample_values": ["Credit card", "Cash", "No charge", "Dispute", "Unknown", "Voided trip"],
                    },
                    "description": {
                        "type": "TEXT",
                        "description": "Additional explanation of when this payment type is used.",
                        "sample_values": ["Payment processed via credit or debit card", "Payment made in cash to driver"],
                    },
                },
            },
            "nyc_rate_codes": {
                "description": "Fare rate codes that determine how the trip fare is calculated.",
                "columns": {
                    "rate_code_id": {
                        "type": "INTEGER",
                        "description": "Numeric rate code used in trip records.",
                        "sample_values": [1, 2, 3, 4, 5, 6],
                    },
                    "rate_code_name": {
                        "type": "VARCHAR",
                        "description": "Name of the rate code.",
                        "sample_values": ["Standard rate", "JFK", "Newark", "Nassau or Westchester", "Negotiated fare", "Group ride"],
                    },
                },
            },
            "nyc_trips": {
                "description": "Individual taxi trips including pickup/dropoff times, locations, fares, and payment details.",
                "columns": {
                    "trip_id": {
                        "type": "BIGINT",
                        "description": "Unique identifier for each trip.",
                        "sample_values": [1, 2, 3, 4, 5],
                    },
                    "pickup_datetime": {
                        "type": "TIMESTAMP",
                        "description": "Date and time when the passenger was picked up.",
                        "sample_values": ["2023-01-01 00:32:10", "2023-01-01 00:55:45", "2023-01-01 01:14:03"],
                    },
                    "dropoff_datetime": {
                        "type": "TIMESTAMP",
                        "description": "Date and time when the passenger was dropped off.",
                        "sample_values": ["2023-01-01 00:40:36", "2023-01-01 01:18:22", "2023-01-01 01:38:47"],
                    },
                    "passenger_count": {
                        "type": "SMALLINT",
                        "description": "Number of passengers in the taxi.",
                        "sample_values": [1, 2, 3, 4, 5, 6],
                    },
                    "trip_distance": {
                        "type": "NUMERIC",
                        "description": "Distance of the trip in miles.",
                        "sample_values": [0.97, 1.10, 2.51, 8.30, 14.70],
                    },
                    "pickup_location_id": {
                        "type": "INTEGER",
                        "description": "Zone where the passenger was picked up. References nyc_taxi_zones.",
                        "sample_values": [161, 236, 90, 132, 170],
                    },
                    "dropoff_location_id": {
                        "type": "INTEGER",
                        "description": "Zone where the passenger was dropped off. References nyc_taxi_zones.",
                        "sample_values": [141, 237, 68, 132, 140],
                    },
                    "payment_type_id": {
                        "type": "INTEGER",
                        "description": "How the fare was paid. References nyc_payment_types.",
                        "sample_values": [1, 2, 1, 2, 1],
                    },
                    "rate_code_id": {
                        "type": "INTEGER",
                        "description": "Fare rate code for the trip. References nyc_rate_codes.",
                        "sample_values": [1, 1, 1, 2, 1],
                    },
                    "fare_amount": {
                        "type": "NUMERIC",
                        "description": "Base metered fare amount in dollars.",
                        "sample_values": [9.30, 7.90, 14.80, 52.00, 35.50],
                    },
                    "tip_amount": {
                        "type": "NUMERIC",
                        "description": "Tip amount in dollars (only automatically populated for credit card payments).",
                        "sample_values": [0.00, 2.00, 3.05, 0.00, 8.15],
                    },
                    "total_amount": {
                        "type": "NUMERIC",
                        "description": "Total amount charged to the passenger including all fees and tips.",
                        "sample_values": [14.30, 12.90, 20.85, 56.50, 47.65],
                    },
                },
            },
        },
        "foreign_keys": [
            {"from_table": "nyc_trips", "from_column": "pickup_location_id", "to_table": "nyc_taxi_zones", "to_column": "location_id"},
            {"from_table": "nyc_trips", "from_column": "dropoff_location_id", "to_table": "nyc_taxi_zones", "to_column": "location_id"},
            {"from_table": "nyc_trips", "from_column": "payment_type_id", "to_table": "nyc_payment_types", "to_column": "payment_type_id"},
            {"from_table": "nyc_trips", "from_column": "rate_code_id", "to_table": "nyc_rate_codes", "to_column": "rate_code_id"},
        ],
    },
}
