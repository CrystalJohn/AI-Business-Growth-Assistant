from fastapi import APIRouter

router = APIRouter(tags=["schema"])

DB_SCHEMA = {
    "tables": [
        {
            "name": "customers",
            "description": "Customer records",
            "columns": [
                {"name": "id", "type": "integer", "pk": True},
                {"name": "name", "type": "varchar"},
                {"name": "email", "type": "varchar"},
                {"name": "segment_id", "type": "integer", "fk": "customer_segments.id"},
                {"name": "city", "type": "varchar"},
                {"name": "country", "type": "varchar"},
                {"name": "lifetime_value", "type": "numeric"},
                {"name": "created_at", "type": "timestamptz"},
            ],
        },
        {
            "name": "customer_segments",
            "description": "Segment definitions",
            "columns": [
                {"name": "id", "type": "integer", "pk": True},
                {"name": "name", "type": "varchar"},
                {"name": "description", "type": "text"},
            ],
        },
        {
            "name": "products",
            "description": "Product catalog",
            "columns": [
                {"name": "id", "type": "integer", "pk": True},
                {"name": "name", "type": "varchar"},
                {"name": "category", "type": "varchar"},
                {"name": "price", "type": "numeric"},
                {"name": "cost", "type": "numeric"},
                {"name": "stock_qty", "type": "integer"},
                {"name": "is_active", "type": "boolean"},
            ],
        },
        {
            "name": "orders",
            "description": "Order headers",
            "columns": [
                {"name": "id", "type": "integer", "pk": True},
                {"name": "customer_id", "type": "integer", "fk": "customers.id"},
                {"name": "status", "type": "varchar"},
                {"name": "total_amount", "type": "numeric"},
                {"name": "discount_amount", "type": "numeric"},
                {"name": "order_date", "type": "timestamptz"},
            ],
        },
        {
            "name": "order_items",
            "description": "Line items per order",
            "columns": [
                {"name": "id", "type": "integer", "pk": True},
                {"name": "order_id", "type": "integer", "fk": "orders.id"},
                {"name": "product_id", "type": "integer", "fk": "products.id"},
                {"name": "quantity", "type": "integer"},
                {"name": "unit_price", "type": "numeric"},
                {"name": "total_price", "type": "numeric"},
            ],
        },
        {
            "name": "campaigns",
            "description": "Marketing campaigns",
            "columns": [
                {"name": "id", "type": "integer", "pk": True},
                {"name": "name", "type": "varchar"},
                {"name": "channel", "type": "varchar"},
                {"name": "budget", "type": "numeric"},
                {"name": "spent", "type": "numeric"},
                {"name": "impressions", "type": "integer"},
                {"name": "clicks", "type": "integer"},
                {"name": "conversions", "type": "integer"},
                {"name": "start_date", "type": "date"},
                {"name": "end_date", "type": "date"},
                {"name": "status", "type": "varchar"},
            ],
        },
        {
            "name": "leads",
            "description": "Sales lead pipeline",
            "columns": [
                {"name": "id", "type": "integer", "pk": True},
                {"name": "name", "type": "varchar"},
                {"name": "email", "type": "varchar"},
                {"name": "source", "type": "varchar"},
                {"name": "campaign_id", "type": "integer", "fk": "campaigns.id"},
                {"name": "status", "type": "varchar"},
                {"name": "score", "type": "integer"},
                {"name": "converted_customer_id", "type": "integer", "fk": "customers.id"},
                {"name": "created_at", "type": "timestamptz"},
                {"name": "converted_at", "type": "timestamptz"},
            ],
        },
    ]
}


@router.get("/schema")
def get_schema():
    return DB_SCHEMA
