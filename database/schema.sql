-- ============================================================
-- AI Business Growth Assistant — Database Schema
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ------------------------------------------------------------
-- customer_segments
-- ------------------------------------------------------------
CREATE TABLE customer_segments (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at  TIMESTAMPTZ  DEFAULT NOW()
);

-- ------------------------------------------------------------
-- customers
-- ------------------------------------------------------------
CREATE TABLE customers (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(200)    NOT NULL,
    email           VARCHAR(255)    UNIQUE NOT NULL,
    phone           VARCHAR(50),
    segment_id      INTEGER         REFERENCES customer_segments(id),
    city            VARCHAR(100),
    country         VARCHAR(100)    DEFAULT 'US',
    lifetime_value  NUMERIC(12, 2)  DEFAULT 0,
    created_at      TIMESTAMPTZ     DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     DEFAULT NOW()
);

-- ------------------------------------------------------------
-- products
-- ------------------------------------------------------------
CREATE TABLE products (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(200)   NOT NULL,
    category    VARCHAR(100),
    price       NUMERIC(10, 2) NOT NULL,
    cost        NUMERIC(10, 2),
    stock_qty   INTEGER        DEFAULT 0,
    is_active   BOOLEAN        DEFAULT TRUE,
    created_at  TIMESTAMPTZ    DEFAULT NOW()
);

-- ------------------------------------------------------------
-- orders
-- ------------------------------------------------------------
CREATE TABLE orders (
    id              SERIAL PRIMARY KEY,
    customer_id     INTEGER         REFERENCES customers(id),
    status          VARCHAR(50)     DEFAULT 'completed',
    total_amount    NUMERIC(12, 2)  DEFAULT 0,
    discount_amount NUMERIC(10, 2)  DEFAULT 0,
    order_date      TIMESTAMPTZ     DEFAULT NOW(),
    shipped_date    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ     DEFAULT NOW()
);

-- ------------------------------------------------------------
-- order_items
-- ------------------------------------------------------------
CREATE TABLE order_items (
    id          SERIAL PRIMARY KEY,
    order_id    INTEGER         REFERENCES orders(id) ON DELETE CASCADE,
    product_id  INTEGER         REFERENCES products(id),
    quantity    INTEGER         NOT NULL DEFAULT 1,
    unit_price  NUMERIC(10, 2)  NOT NULL,
    total_price NUMERIC(12, 2)  GENERATED ALWAYS AS (quantity * unit_price) STORED
);

-- ------------------------------------------------------------
-- campaigns
-- ------------------------------------------------------------
CREATE TABLE campaigns (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(200)   NOT NULL,
    channel     VARCHAR(100),
    budget      NUMERIC(12, 2),
    spent       NUMERIC(12, 2) DEFAULT 0,
    impressions INTEGER        DEFAULT 0,
    clicks      INTEGER        DEFAULT 0,
    conversions INTEGER        DEFAULT 0,
    start_date  DATE,
    end_date    DATE,
    status      VARCHAR(50)    DEFAULT 'active',
    created_at  TIMESTAMPTZ    DEFAULT NOW()
);

-- ------------------------------------------------------------
-- leads
-- ------------------------------------------------------------
CREATE TABLE leads (
    id                    SERIAL PRIMARY KEY,
    name                  VARCHAR(200) NOT NULL,
    email                 VARCHAR(255),
    phone                 VARCHAR(50),
    source                VARCHAR(100),
    campaign_id           INTEGER      REFERENCES campaigns(id),
    status                VARCHAR(50)  DEFAULT 'new',
    score                 INTEGER      DEFAULT 0,
    converted_customer_id INTEGER      REFERENCES customers(id),
    created_at            TIMESTAMPTZ  DEFAULT NOW(),
    converted_at          TIMESTAMPTZ
);

-- ------------------------------------------------------------
-- Indexes
-- ------------------------------------------------------------
CREATE INDEX idx_customers_segment_id   ON customers(segment_id);
CREATE INDEX idx_orders_customer_id     ON orders(customer_id);
CREATE INDEX idx_orders_order_date      ON orders(order_date);
CREATE INDEX idx_order_items_order_id   ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
CREATE INDEX idx_leads_campaign_id      ON leads(campaign_id);
CREATE INDEX idx_leads_status           ON leads(status);
CREATE INDEX idx_leads_source           ON leads(source);
