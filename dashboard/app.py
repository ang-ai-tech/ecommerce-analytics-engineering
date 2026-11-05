"""Sales dashboard on the dbt marts. Run: streamlit run dashboard/app.py"""

from __future__ import annotations

import os
from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

DEFAULT_WAREHOUSE = Path(__file__).resolve().parents[1] / "data" / "warehouse.duckdb"
WAREHOUSE = Path(os.environ.get("SHOP_WAREHOUSE", DEFAULT_WAREHOUSE))

st.set_page_config(page_title="Online store analytics", layout="wide")


@st.cache_data(ttl=60)
def query(sql: str) -> pd.DataFrame:
    # Open and close the connection each time, so `dbt build` can write to the file.
    with duckdb.connect(str(WAREHOUSE), read_only=True) as connection:
        return connection.sql(sql).df()


st.title("Online store analytics")
st.caption("Fictional online store selling home and office products. All data is synthetic.")

if not WAREHOUSE.exists():
    st.error("No warehouse found. Run `shopdata generate` and then `dbt build` first.")
    st.stop()

monthly = query("select * from marts.rpt_monthly_sales order by order_month")
customers = query(
    "select customer_type, count(*) as customers from marts.dim_customers group by customer_type"
)

# ---- KPIs -------------------------------------------------------------------------------
buyers = customers.set_index("customer_type")["customers"]
repeat_share = buyers.get("repeat", 0) / (buyers.get("repeat", 0) + buyers.get("one-time", 0))

kpi = st.columns(4)
kpi[0].metric("Revenue", f"€ {monthly['revenue'].sum():,.0f}")
kpi[1].metric("Completed orders", f"{monthly['orders'].sum():,}")
kpi[2].metric("Average order value", f"€ {monthly['revenue'].sum() / monthly['orders'].sum():.2f}")
kpi[3].metric("Repeat customers", f"{repeat_share:.0%}", help="Buyers with 2+ completed orders")

# ---- Sales over time ----------------------------------------------------------------------
left, right = st.columns(2)
with left:
    st.subheader("Revenue per month")
    st.line_chart(monthly, x="order_month", y="revenue")
with right:
    st.subheader("New and returning customers")
    st.bar_chart(monthly, x="order_month", y=["new_customers", "returning_customers"])

# ---- Categories and funnel ------------------------------------------------------------------
left, right = st.columns(2)
with left:
    st.subheader("Revenue per category")
    categories = query(
        "select category, sum(revenue) as revenue from marts.rpt_category_sales "
        "group by category order by revenue desc"
    )
    st.bar_chart(categories, x="category", y="revenue", horizontal=True, sort="-revenue")
with right:
    st.subheader("Purchase funnel (all visits)")
    funnel = query(
        "select sum(sessions) as visits, sum(sessions_with_cart) as cart, "
        "sum(sessions_with_checkout) as checkout, sum(sessions_with_purchase) as purchase "
        "from marts.rpt_funnel_monthly"
    ).T.reset_index()
    funnel.columns = ["step", "visits"]
    funnel["share of visits"] = (funnel["visits"] / funnel["visits"].iloc[0]).map("{:.1%}".format)
    st.bar_chart(funnel, x="step", y="visits", sort=False)
    st.dataframe(funnel, hide_index=True, width="stretch")

# ---- Cohorts --------------------------------------------------------------------------------
st.subheader("Cohort retention")
st.caption(
    "Each row is the month of a customer's first purchase. Each column shows the share of "
    "those customers who bought again N months later."
)
cohorts = query(
    "select cohort_month, months_since_first_purchase, retention_rate "
    "from marts.rpt_cohort_retention where months_since_first_purchase <= 6"
)
table = cohorts.pivot(
    index="cohort_month", columns="months_since_first_purchase", values="retention_rate"
).astype(float)
# A month with no repeat buyers is 0%; a month that has not happened yet stays empty.
last_month = pd.to_datetime(monthly["order_month"]).max()
for cohort in table.index:
    months_observed = (last_month.year - cohort.year) * 12 + last_month.month - cohort.month
    for months in table.columns:
        if months <= months_observed and pd.isna(table.loc[cohort, months]):
            table.loc[cohort, months] = 0.0
table.index = pd.to_datetime(table.index).strftime("%Y-%m")
table.columns = [f"month {n}" for n in table.columns]
st.dataframe(table.style.format("{:.0%}", na_rep=""), width="stretch")
