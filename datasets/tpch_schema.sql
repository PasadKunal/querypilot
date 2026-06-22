-- TPC-H schema: industry-standard analytical benchmark database.
-- Used to test complex joins, aggregations, and performance on large datasets.

CREATE TABLE IF NOT EXISTS tpch_region (
    r_regionkey INTEGER PRIMARY KEY,
    r_name      VARCHAR(25)  NOT NULL,
    r_comment   VARCHAR(152)
);

CREATE TABLE IF NOT EXISTS tpch_nation (
    n_nationkey INTEGER PRIMARY KEY,
    n_name      VARCHAR(25)  NOT NULL,
    n_regionkey INTEGER      NOT NULL REFERENCES tpch_region(r_regionkey),
    n_comment   VARCHAR(152)
);

CREATE TABLE IF NOT EXISTS tpch_customer (
    c_custkey       INTEGER         PRIMARY KEY,
    c_name          VARCHAR(25)     NOT NULL,
    c_address       VARCHAR(40)     NOT NULL,
    c_nationkey     INTEGER         NOT NULL REFERENCES tpch_nation(n_nationkey),
    c_phone         VARCHAR(15)     NOT NULL,
    c_acctbal       NUMERIC(15,2)   NOT NULL,
    c_mktsegment    VARCHAR(10),
    c_comment       VARCHAR(117)
);

CREATE TABLE IF NOT EXISTS tpch_supplier (
    s_suppkey   INTEGER         PRIMARY KEY,
    s_name      VARCHAR(25)     NOT NULL,
    s_address   VARCHAR(40)     NOT NULL,
    s_nationkey INTEGER         NOT NULL REFERENCES tpch_nation(n_nationkey),
    s_phone     VARCHAR(15)     NOT NULL,
    s_acctbal   NUMERIC(15,2)   NOT NULL,
    s_comment   VARCHAR(101)
);

CREATE TABLE IF NOT EXISTS tpch_part (
    p_partkey       INTEGER         PRIMARY KEY,
    p_name          VARCHAR(55)     NOT NULL,
    p_mfgr          VARCHAR(25),
    p_brand         VARCHAR(10),
    p_type          VARCHAR(25),
    p_size          INTEGER,
    p_container     VARCHAR(10),
    p_retailprice   NUMERIC(15,2),
    p_comment       VARCHAR(23)
);

CREATE TABLE IF NOT EXISTS tpch_partsupp (
    ps_partkey      INTEGER         NOT NULL REFERENCES tpch_part(p_partkey),
    ps_suppkey      INTEGER         NOT NULL REFERENCES tpch_supplier(s_suppkey),
    ps_availqty     INTEGER         NOT NULL,
    ps_supplycost   NUMERIC(15,2)   NOT NULL,
    ps_comment      VARCHAR(199),
    PRIMARY KEY (ps_partkey, ps_suppkey)
);

CREATE TABLE IF NOT EXISTS tpch_orders (
    o_orderkey      INTEGER         PRIMARY KEY,
    o_custkey       INTEGER         NOT NULL REFERENCES tpch_customer(c_custkey),
    o_orderstatus   CHAR(1)         NOT NULL,
    o_totalprice    NUMERIC(15,2)   NOT NULL,
    o_orderdate     DATE            NOT NULL,
    o_orderpriority VARCHAR(15),
    o_clerk         VARCHAR(15),
    o_shippriority  INTEGER,
    o_comment       VARCHAR(79)
);

CREATE TABLE IF NOT EXISTS tpch_lineitem (
    l_orderkey          INTEGER         NOT NULL REFERENCES tpch_orders(o_orderkey),
    l_partkey           INTEGER         NOT NULL,
    l_suppkey           INTEGER         NOT NULL,
    l_linenumber        INTEGER         NOT NULL,
    l_quantity          NUMERIC(15,2)   NOT NULL,
    l_extendedprice     NUMERIC(15,2)   NOT NULL,
    l_discount          NUMERIC(15,2)   NOT NULL,
    l_tax               NUMERIC(15,2)   NOT NULL,
    l_returnflag        CHAR(1),
    l_linestatus        CHAR(1),
    l_shipdate          DATE            NOT NULL,
    l_commitdate        DATE,
    l_receiptdate       DATE,
    l_shipinstruct      VARCHAR(25),
    l_shipmode          VARCHAR(10),
    l_comment           VARCHAR(44),
    PRIMARY KEY (l_orderkey, l_linenumber),
    FOREIGN KEY (l_partkey, l_suppkey) REFERENCES tpch_partsupp(ps_partkey, ps_suppkey)
);
