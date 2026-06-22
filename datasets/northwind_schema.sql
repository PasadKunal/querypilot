-- Northwind schema: classic trading company database.
-- Used to test multi-table joins, aggregations, and business analytics queries.

CREATE TABLE IF NOT EXISTS nw_categories (
    category_id     SERIAL PRIMARY KEY,
    category_name   VARCHAR(15)  NOT NULL,
    description     TEXT
);

CREATE TABLE IF NOT EXISTS nw_suppliers (
    supplier_id     SERIAL PRIMARY KEY,
    company_name    VARCHAR(40)  NOT NULL,
    contact_name    VARCHAR(30),
    contact_title   VARCHAR(30),
    address         VARCHAR(60),
    city            VARCHAR(15),
    region          VARCHAR(15),
    postal_code     VARCHAR(10),
    country         VARCHAR(15),
    phone           VARCHAR(24),
    fax             VARCHAR(24)
);

CREATE TABLE IF NOT EXISTS nw_shippers (
    shipper_id      SERIAL PRIMARY KEY,
    company_name    VARCHAR(40)  NOT NULL,
    phone           VARCHAR(24)
);

CREATE TABLE IF NOT EXISTS nw_employees (
    employee_id     SERIAL PRIMARY KEY,
    last_name       VARCHAR(20)  NOT NULL,
    first_name      VARCHAR(10)  NOT NULL,
    title           VARCHAR(30),
    birth_date      DATE,
    hire_date       DATE,
    address         VARCHAR(60),
    city            VARCHAR(15),
    region          VARCHAR(15),
    postal_code     VARCHAR(10),
    country         VARCHAR(15),
    home_phone      VARCHAR(24),
    reports_to      INTEGER REFERENCES nw_employees(employee_id)
);

CREATE TABLE IF NOT EXISTS nw_customers (
    customer_id     VARCHAR(5)   PRIMARY KEY,
    company_name    VARCHAR(40)  NOT NULL,
    contact_name    VARCHAR(30),
    contact_title   VARCHAR(30),
    address         VARCHAR(60),
    city            VARCHAR(15),
    region          VARCHAR(15),
    postal_code     VARCHAR(10),
    country         VARCHAR(15),
    phone           VARCHAR(24),
    fax             VARCHAR(24)
);

CREATE TABLE IF NOT EXISTS nw_products (
    product_id          SERIAL PRIMARY KEY,
    product_name        VARCHAR(40)     NOT NULL,
    supplier_id         INTEGER         REFERENCES nw_suppliers(supplier_id),
    category_id         INTEGER         REFERENCES nw_categories(category_id),
    quantity_per_unit   VARCHAR(20),
    unit_price          NUMERIC(10,2)   DEFAULT 0,
    units_in_stock      SMALLINT        DEFAULT 0,
    units_on_order      SMALLINT        DEFAULT 0,
    reorder_level       SMALLINT        DEFAULT 0,
    discontinued        BOOLEAN         NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS nw_orders (
    order_id            SERIAL PRIMARY KEY,
    customer_id         VARCHAR(5)      REFERENCES nw_customers(customer_id),
    employee_id         INTEGER         REFERENCES nw_employees(employee_id),
    order_date          DATE,
    required_date       DATE,
    shipped_date        DATE,
    ship_via            INTEGER         REFERENCES nw_shippers(shipper_id),
    freight             NUMERIC(10,2)   DEFAULT 0,
    ship_name           VARCHAR(40),
    ship_address        VARCHAR(60),
    ship_city           VARCHAR(15),
    ship_region         VARCHAR(15),
    ship_postal_code    VARCHAR(10),
    ship_country        VARCHAR(15)
);

CREATE TABLE IF NOT EXISTS nw_order_details (
    order_id    INTEGER         NOT NULL REFERENCES nw_orders(order_id),
    product_id  INTEGER         NOT NULL REFERENCES nw_products(product_id),
    unit_price  NUMERIC(10,2)   NOT NULL DEFAULT 0,
    quantity    SMALLINT        NOT NULL DEFAULT 1,
    discount    REAL            NOT NULL DEFAULT 0,
    PRIMARY KEY (order_id, product_id)
);
