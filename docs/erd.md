# Entity Relationship Diagram

```mermaid
erDiagram
    customer_segments {
        int id PK
        varchar name
        text description
        timestamptz created_at
    }

    customers {
        int id PK
        varchar name
        varchar email
        varchar phone
        int segment_id FK
        varchar city
        varchar country
        numeric lifetime_value
        timestamptz created_at
        timestamptz updated_at
    }

    products {
        int id PK
        varchar name
        varchar category
        numeric price
        numeric cost
        int stock_qty
        boolean is_active
        timestamptz created_at
    }

    orders {
        int id PK
        int customer_id FK
        varchar status
        numeric total_amount
        numeric discount_amount
        timestamptz order_date
        timestamptz shipped_date
        timestamptz created_at
    }

    order_items {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        numeric unit_price
        numeric total_price
    }

    campaigns {
        int id PK
        varchar name
        varchar channel
        numeric budget
        numeric spent
        int impressions
        int clicks
        int conversions
        date start_date
        date end_date
        varchar status
        timestamptz created_at
    }

    leads {
        int id PK
        varchar name
        varchar email
        varchar phone
        varchar source
        int campaign_id FK
        varchar status
        int score
        int converted_customer_id FK
        timestamptz created_at
        timestamptz converted_at
    }

    customer_segments ||--o{ customers : "has"
    customers         ||--o{ orders    : "places"
    orders            ||--o{ order_items : "contains"
    products          ||--o{ order_items : "appears in"
    campaigns         ||--o{ leads     : "generates"
    customers         ||--o{ leads     : "converted from"
```

## Key Relationships

| Relationship | Cardinality | Notes |
|---|---|---|
| `customer_segments` → `customers` | 1:N | Each customer belongs to one segment |
| `customers` → `orders` | 1:N | A customer can have many orders |
| `orders` → `order_items` | 1:N | Each order has one or more line items |
| `products` → `order_items` | 1:N | A product can appear in many order items |
| `campaigns` → `leads` | 1:N | A campaign generates many leads |
| `leads` → `customers` | N:1 (optional) | A converted lead becomes a customer |

## Analytics Queries Enabled

- **Revenue** — `SUM(orders.total_amount)` grouped by month, segment, product
- **Product performance** — `JOIN order_items ON products` → revenue, volume
- **Customer LTV** — `customers.lifetime_value` or computed from orders
- **Campaign ROI** — `campaigns.conversions / campaigns.spent`
- **Lead funnel** — `leads.status` counts by `source`, `campaign_id`
- **Segment analysis** — `JOIN customers ON customer_segments`
