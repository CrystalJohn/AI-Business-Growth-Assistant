"""
Mock LLM provider.

Returns realistic pre-canned responses based on keyword matching.
Replace this module with a real LLM provider when ready.
"""

from app.models import QueryResponse, TableColumn

# ---------------------------------------------------------------------------
# Response catalogue
# ---------------------------------------------------------------------------

_RESPONSES: list[dict] = [
    {
        "keywords": ["top", "product", "revenue", "best", "selling"],
        "answer": (
            "The top 5 products by total revenue are led by **White-label License** "
            "and **Analytics Enterprise**, which together account for over 60% of total "
            "product revenue. Software subscriptions dominate the mix."
        ),
        "sql": """\
SELECT
  p.name                          AS product,
  p.category,
  SUM(oi.total_price)             AS total_revenue,
  COUNT(DISTINCT oi.order_id)     AS orders_count
FROM order_items  oi
JOIN products     p  ON p.id = oi.product_id
GROUP BY p.id, p.name, p.category
ORDER BY total_revenue DESC
LIMIT 5;""",
        "columns": [
            {"key": "product", "label": "Product", "type": "string"},
            {"key": "category", "label": "Category", "type": "string"},
            {"key": "total_revenue", "label": "Revenue ($)", "type": "number"},
            {"key": "orders_count", "label": "Orders", "type": "number"},
        ],
        "rows": [
            {"product": "White-label License",   "category": "License",  "total_revenue": 74975.00, "orders_count": 25},
            {"product": "Analytics Enterprise",  "category": "Software", "total_revenue": 52947.00, "orders_count": 53},
            {"product": "Setup & Onboarding",    "category": "Services", "total_revenue": 31500.00, "orders_count": 21},
            {"product": "Analytics Pro",         "category": "Software", "total_revenue": 23022.00, "orders_count": 77},
            {"product": "AI Insights Module",    "category": "Add-on",   "total_revenue": 10547.00, "orders_count": 53},
        ],
        "chartType": "bar",
        "followUpQuestions": [
            "Which customer segment buys the most White-label Licenses?",
            "What is the profit margin per product category?",
            "How has product revenue trended month over month?",
        ],
    },
    {
        "keywords": ["monthly", "revenue", "trend", "month", "over"],
        "answer": (
            "Monthly revenue has grown steadily throughout 2024, starting at **$31,195** "
            "in January and peaking at **$49,730** in December — a **59% increase** over "
            "the year. Q4 showed the strongest growth, driven by the Fall Product Launch campaign."
        ),
        "sql": """\
SELECT
  TO_CHAR(order_date, 'YYYY-MM')  AS month,
  SUM(total_amount)               AS revenue,
  COUNT(*)                        AS order_count
FROM orders
WHERE order_date >= '2024-01-01'
GROUP BY 1
ORDER BY 1;""",
        "columns": [
            {"key": "month",       "label": "Month",       "type": "string"},
            {"key": "revenue",     "label": "Revenue ($)", "type": "number"},
            {"key": "order_count", "label": "Orders",      "type": "number"},
        ],
        "rows": [
            {"month": "2024-01", "revenue": 31195.00, "order_count":  8},
            {"month": "2024-02", "revenue": 28568.00, "order_count":  8},
            {"month": "2024-03", "revenue": 33496.00, "order_count":  8},
            {"month": "2024-04", "revenue": 30316.00, "order_count":  8},
            {"month": "2024-05", "revenue": 35016.00, "order_count":  8},
            {"month": "2024-06", "revenue": 36988.00, "order_count":  8},
            {"month": "2024-07", "revenue": 38073.00, "order_count":  8},
            {"month": "2024-08", "revenue": 36464.00, "order_count":  8},
            {"month": "2024-09", "revenue": 40586.00, "order_count":  8},
            {"month": "2024-10", "revenue": 43863.00, "order_count":  8},
            {"month": "2024-11", "revenue": 45984.00, "order_count":  8},
            {"month": "2024-12", "revenue": 49730.00, "order_count":  8},
        ],
        "chartType": "line",
        "followUpQuestions": [
            "Which months had the highest average order value?",
            "What drove the revenue spike in Q4?",
            "Break down monthly revenue by customer segment.",
        ],
    },
    {
        "keywords": ["segment", "customer", "value", "ltv", "lifetime"],
        "answer": (
            "**Partner** customers have the highest average lifetime value at **$20,783**, "
            "followed by Enterprise at **$27,350** (highest total). Individual customers "
            "have the lowest LTV at ~**$1,013** but represent the largest segment by count."
        ),
        "sql": """\
SELECT
  cs.name                        AS segment,
  COUNT(c.id)                    AS customer_count,
  ROUND(AVG(c.lifetime_value), 2) AS avg_ltv,
  SUM(c.lifetime_value)          AS total_ltv
FROM customers        c
JOIN customer_segments cs ON cs.id = c.segment_id
GROUP BY cs.name
ORDER BY avg_ltv DESC;""",
        "columns": [
            {"key": "segment",        "label": "Segment",         "type": "string"},
            {"key": "customer_count", "label": "Customers",       "type": "number"},
            {"key": "avg_ltv",        "label": "Avg LTV ($)",     "type": "number"},
            {"key": "total_ltv",      "label": "Total LTV ($)",   "type": "number"},
        ],
        "rows": [
            {"segment": "Partner",    "customer_count": 6, "avg_ltv": 20783.33, "total_ltv": 124700.00},
            {"segment": "Enterprise", "customer_count": 6, "avg_ltv": 27350.00, "total_ltv": 164100.00},
            {"segment": "SMB",        "customer_count": 6, "avg_ltv":  9266.67, "total_ltv":  55600.00},
            {"segment": "Startup",    "customer_count": 6, "avg_ltv":  3016.67, "total_ltv":  18100.00},
            {"segment": "Individual", "customer_count": 6, "avg_ltv":  1013.33, "total_ltv":   6080.00},
        ],
        "chartType": "bar",
        "followUpQuestions": [
            "What products do Enterprise customers buy most?",
            "How many customers churned in each segment this year?",
            "What is the revenue contribution of each segment?",
        ],
    },
    {
        "keywords": ["campaign", "performance", "conversion", "roi", "best"],
        "answer": (
            "The **Fall Product Launch** campaign had the highest conversions (340) with a "
            "strong ROI. **Partner Referral Q3** achieved the best conversion rate at **15.8%** "
            "with the lowest cost per conversion. Google Ads campaigns drove the most volume."
        ),
        "sql": """\
SELECT
  name,
  channel,
  budget,
  spent,
  conversions,
  ROUND(conversions::numeric / NULLIF(clicks, 0) * 100, 2) AS conversion_rate_pct,
  ROUND(spent / NULLIF(conversions, 0), 2)                  AS cost_per_conversion
FROM campaigns
ORDER BY conversions DESC;""",
        "columns": [
            {"key": "name",                 "label": "Campaign",          "type": "string"},
            {"key": "channel",              "label": "Channel",           "type": "string"},
            {"key": "conversions",          "label": "Conversions",       "type": "number"},
            {"key": "conversion_rate_pct",  "label": "Conv. Rate (%)",    "type": "number"},
            {"key": "cost_per_conversion",  "label": "Cost/Conv. ($)",    "type": "number"},
        ],
        "rows": [
            {"name": "Fall Product Launch",   "channel": "Multi-channel", "conversions": 340, "conversion_rate_pct": 1.89, "cost_per_conversion":  64.71},
            {"name": "Q3 Google Ads",         "channel": "Google Ads",    "conversions": 265, "conversion_rate_pct": 2.60, "cost_per_conversion":  65.66},
            {"name": "Q1 Google Ads",         "channel": "Google Ads",    "conversions": 210, "conversion_rate_pct": 2.50, "cost_per_conversion":  67.62},
            {"name": "Q4 Year-End Push",      "channel": "Email",         "conversions": 210, "conversion_rate_pct": 1.48, "cost_per_conversion":  17.14},
            {"name": "Summer Social Ads",     "channel": "Facebook",      "conversions": 198, "conversion_rate_pct": 1.65, "cost_per_conversion":  47.98},
            {"name": "Webinar Series Q2",     "channel": "Webinar",       "conversions": 120, "conversion_rate_pct": 8.57, "cost_per_conversion":  26.67},
            {"name": "Partner Referral Q3",   "channel": "Referral",      "conversions":  95, "conversion_rate_pct":15.83, "cost_per_conversion":   8.42},
            {"name": "Spring Email Blast",    "channel": "Email",         "conversions": 145, "conversion_rate_pct": 1.48, "cost_per_conversion":  12.41},
            {"name": "Q1 LinkedIn Outreach",  "channel": "LinkedIn",      "conversions":  88, "conversion_rate_pct": 2.75, "cost_per_conversion":  86.36},
            {"name": "Q2 Content Marketing",  "channel": "Content",       "conversions":  73, "conversion_rate_pct": 1.18, "cost_per_conversion":  67.12},
        ],
        "chartType": "bar",
        "followUpQuestions": [
            "Which campaign channel has the best overall ROI?",
            "How many leads did each campaign generate?",
            "What was the total marketing spend vs revenue generated?",
        ],
    },
    {
        "keywords": ["lead", "conversion", "source", "pipeline", "funnel"],
        "answer": (
            "The sales pipeline shows **60 leads** total. **Referral** leads have the highest "
            "conversion rate at **60%**, while Google Ads drives the most volume. "
            "Currently 14 leads are in qualified status, ready for follow-up."
        ),
        "sql": """\
SELECT
  source,
  COUNT(*)                                                          AS total_leads,
  SUM(CASE WHEN status = 'converted' THEN 1 ELSE 0 END)           AS converted,
  SUM(CASE WHEN status = 'qualified' THEN 1 ELSE 0 END)           AS qualified,
  SUM(CASE WHEN status = 'lost'      THEN 1 ELSE 0 END)           AS lost,
  ROUND(
    SUM(CASE WHEN status = 'converted' THEN 1 ELSE 0 END)::numeric
    / COUNT(*) * 100, 1
  )                                                                 AS conversion_rate_pct
FROM leads
GROUP BY source
ORDER BY total_leads DESC;""",
        "columns": [
            {"key": "source",              "label": "Source",          "type": "string"},
            {"key": "total_leads",         "label": "Total Leads",     "type": "number"},
            {"key": "converted",           "label": "Converted",       "type": "number"},
            {"key": "qualified",           "label": "Qualified",       "type": "number"},
            {"key": "lost",                "label": "Lost",            "type": "number"},
            {"key": "conversion_rate_pct", "label": "Conv. Rate (%)", "type": "number"},
        ],
        "rows": [
            {"source": "Google Ads", "total_leads": 16, "converted":  8, "qualified": 3, "lost": 4, "conversion_rate_pct": 50.0},
            {"source": "Facebook",   "total_leads": 10, "converted":  4, "qualified": 3, "lost": 3, "conversion_rate_pct": 40.0},
            {"source": "LinkedIn",   "total_leads": 10, "converted":  2, "qualified": 3, "lost": 3, "conversion_rate_pct": 20.0},
            {"source": "Content",    "total_leads":  8, "converted":  3, "qualified": 1, "lost": 2, "conversion_rate_pct": 37.5},
            {"source": "Referral",   "total_leads":  8, "converted":  5, "qualified": 2, "lost": 1, "conversion_rate_pct": 62.5},
            {"source": "Email",      "total_leads":  6, "converted":  2, "qualified": 2, "lost": 0, "conversion_rate_pct": 33.3},
            {"source": "Webinar",    "total_leads":  5, "converted":  2, "qualified": 1, "lost": 1, "conversion_rate_pct": 40.0},
        ],
        "chartType": "bar",
        "followUpQuestions": [
            "What is the average lead score by source?",
            "Which campaigns generated the most qualified leads?",
            "How long does it take on average to convert a lead?",
        ],
    },
    {
        "keywords": ["order", "average", "value", "aov", "basket"],
        "answer": (
            "The average order value (AOV) across all completed orders is **$3,847**. "
            "Partner-segment orders have the highest AOV at **$5,210**, while Individual "
            "customers average **$487** per order."
        ),
        "sql": """\
SELECT
  cs.name                           AS segment,
  COUNT(o.id)                       AS total_orders,
  ROUND(AVG(o.total_amount), 2)     AS avg_order_value,
  ROUND(SUM(o.total_amount), 2)     AS total_revenue
FROM orders           o
JOIN customers        c  ON c.id = o.customer_id
JOIN customer_segments cs ON cs.id = c.segment_id
WHERE o.status = 'completed'
GROUP BY cs.name
ORDER BY avg_order_value DESC;""",
        "columns": [
            {"key": "segment",         "label": "Segment",       "type": "string"},
            {"key": "total_orders",    "label": "Orders",        "type": "number"},
            {"key": "avg_order_value", "label": "Avg AOV ($)",   "type": "number"},
            {"key": "total_revenue",   "label": "Revenue ($)",   "type": "number"},
        ],
        "rows": [
            {"segment": "Partner",    "total_orders": 26, "avg_order_value": 5188.46, "total_revenue": 134900.00},
            {"segment": "Enterprise", "total_orders": 28, "avg_order_value": 4571.43, "total_revenue": 128000.00},
            {"segment": "SMB",        "total_orders": 22, "avg_order_value": 2372.73, "total_revenue":  52200.00},
            {"segment": "Startup",    "total_orders": 14, "avg_order_value":  897.14, "total_revenue":  12560.00},
            {"segment": "Individual", "total_orders":  6, "avg_order_value":  487.00, "total_revenue":   2922.00},
        ],
        "chartType": "bar",
        "followUpQuestions": [
            "Which individual customers have placed the most orders?",
            "What is the AOV trend over the last 6 months?",
            "How does discount usage impact average order value?",
        ],
    },
]

# ---------------------------------------------------------------------------
# Default fallback
# ---------------------------------------------------------------------------

_DEFAULT_RESPONSE: dict = {
    "answer": (
        "Based on the available business data, I can provide insights on revenue trends, "
        "product performance, customer segments, campaign effectiveness, and lead pipeline. "
        "Try asking something like: *'What are our top products by revenue?'* or "
        "*'Show me monthly revenue for 2024.'*"
    ),
    "sql": """\
SELECT
  'customers'      AS table_name, COUNT(*) AS row_count FROM customers
UNION ALL
SELECT 'products',    COUNT(*) FROM products
UNION ALL
SELECT 'orders',      COUNT(*) FROM orders
UNION ALL
SELECT 'leads',       COUNT(*) FROM leads
UNION ALL
SELECT 'campaigns',   COUNT(*) FROM campaigns;""",
    "columns": [
        {"key": "table_name", "label": "Table",     "type": "string"},
        {"key": "row_count",  "label": "Row Count", "type": "number"},
    ],
    "rows": [
        {"table_name": "customers",  "row_count": 30},
        {"table_name": "products",   "row_count": 15},
        {"table_name": "orders",     "row_count": 96},
        {"table_name": "leads",      "row_count": 60},
        {"table_name": "campaigns",  "row_count": 10},
    ],
    "chartType": "bar",
    "followUpQuestions": [
        "What are the top 5 products by revenue?",
        "Show me monthly revenue trends for 2024.",
        "Which customer segment has the highest lifetime value?",
        "How are our marketing campaigns performing?",
        "What is our lead conversion rate by source?",
    ],
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_mock_response(question: str) -> QueryResponse:
    q = question.lower()

    for resp in _RESPONSES:
        if any(kw in q for kw in resp["keywords"]):
            return QueryResponse(
                answer=resp["answer"],
                sql=resp["sql"],
                columns=[TableColumn(**c) for c in resp["columns"]],
                rows=resp["rows"],
                chartType=resp.get("chartType"),
                followUpQuestions=resp.get("followUpQuestions", []),
            )

    return QueryResponse(
        answer=_DEFAULT_RESPONSE["answer"],
        sql=_DEFAULT_RESPONSE["sql"],
        columns=[TableColumn(**c) for c in _DEFAULT_RESPONSE["columns"]],
        rows=_DEFAULT_RESPONSE["rows"],
        chartType=_DEFAULT_RESPONSE.get("chartType"),
        followUpQuestions=_DEFAULT_RESPONSE.get("followUpQuestions", []),
    )
