"""
Logistics Delivery Performance & Cost Analytics
Compact Streamlit dashboard.
"""

from pathlib import Path
import pandas as pd
import streamlit as st

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Logistics Delivery Performance & Cost Analytics",
    page_icon="🚚",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ============================================================
# STYLING
# ============================================================

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1150px;
        margin: auto;
        padding-top: 1.4rem;
        padding-bottom: 2rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }

    .dashboard-title {
        font-size: 34px;
        font-weight: 800;
        margin-bottom: 6px;
    }

    .dashboard-subtitle {
        font-size: 14px;
        font-weight: 500;
        color: #aeb4c0;
        margin-bottom: 22px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 800;
        margin-top: 22px;
        margin-bottom: 16px;
    }

    .subsection-title {
        font-size: 18px;
        font-weight: 700;
        margin-top: 18px;
        margin-bottom: 10px;
    }

    .kpi-card {
        background: #151922;
        border: 1px solid #303642;
        border-radius: 12px;
        padding: 16px 17px;
        min-height: 128px;
        margin-bottom: 16px;
    }

    .kpi-title {
        font-size: 15px;
        font-weight: 700;
        color: #e8eaf0;
        margin-bottom: 7px;
    }

    .kpi-value {
        font-size: 27px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 5px;
    }

    .kpi-description {
        font-size: 12px;
        font-weight: 400;
        color: #9da4b2;
        line-height: 1.35;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        font-weight: 800;
    }

    [data-testid="stMetricLabel"] {
        font-size: 13px !important;
        font-weight: 600 !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 25px !important;
        font-weight: 800 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="dashboard-title">🚚 Logistics Delivery Performance & Cost Analytics</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="dashboard-subtitle">Interactive analysis of delivery performance, logistics cost, warehouses, transport modes, products and routes.</div>',
    unsafe_allow_html=True,
)

# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLEANED_DATA_PATH = PROJECT_ROOT / "data" / "cleaned" / "logistics_cleaned.csv"

# ============================================================
# GENERAL HELPERS
# ============================================================

def format_number(value):
    """Format a numeric value with thousands separators."""
    if pd.isna(value):
        return "0"
    return f"{value:,.0f}"


def format_currency(value):
    """Format a numeric value as Indian currency."""
    if pd.isna(value):
        return "₹0.00"
    return f"₹{value:,.2f}"


def format_percentage(value):
    """Format a percentage value."""
    if pd.isna(value):
        return "0.0%"
    return f"{value:.1f}%"


def create_kpi_card(title, value, description):
    """Display one styled KPI card."""
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-description">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(title):
    """Display a large bold section heading."""
    st.markdown(
        f'<div class="section-title">{title}</div>',
        unsafe_allow_html=True,
    )


def subsection_title(title):
    """Display a smaller bold subsection heading."""
    st.markdown(
        f'<div class="subsection-title">{title}</div>',
        unsafe_allow_html=True,
    )

# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_dashboard_data():
    """Load and prepare the cleaned logistics dataset."""
    if not CLEANED_DATA_PATH.exists():
        st.error(
            "Cleaned dataset was not found. "
            "Run the pipeline first to create data/cleaned/logistics_cleaned.csv."
        )
        st.stop()

    df = pd.read_csv(CLEANED_DATA_PATH)

    date_columns = [
        "order_date",
        "dispatch_date",
        "expected_delivery_date",
        "actual_delivery_date",
    ]

    for column in date_columns:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce")

    numeric_columns = [
        "distance_km",
        "quantity",
        "weight_kg",
        "shipping_cost",
        "fuel_cost",
        "warehouse_processing_hours",
        "customer_rating",
        "damage_flag",
        "return_flag",
        "delivery_days",
        "delay_days",
        "cost_per_km",
        "total_logistics_cost",
        "on_time_flag",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    return df

# ============================================================
# KPI CALCULATIONS
# ============================================================

def calculate_kpis(df):
    """Calculate the main dashboard KPIs."""
    result = {}

    result["total_orders"] = df["order_id"].nunique() if "order_id" in df else len(df)

    if "delivery_status" in df:
        status = df["delivery_status"].astype(str).str.lower()
        result["delivered_orders"] = int(status.eq("delivered").sum())
        result["delayed_orders"] = int(status.eq("delayed").sum())
    else:
        result["delivered_orders"] = 0
        result["delayed_orders"] = 0

    if "on_time_flag" in df:
        result["on_time_rate"] = df["on_time_flag"].mean() * 100
    elif "delivery_status" in df:
        status = df["delivery_status"].astype(str).str.lower()
        result["on_time_rate"] = status.eq("delivered").mean() * 100
    else:
        result["on_time_rate"] = 0

    result["avg_delivery_days"] = (
        df["delivery_days"].mean() if "delivery_days" in df else 0
    )

    result["avg_cost"] = (
        df["total_logistics_cost"].mean()
        if "total_logistics_cost" in df
        else 0
    )

    result["total_cost"] = (
        df["total_logistics_cost"].sum()
        if "total_logistics_cost" in df
        else 0
    )

    result["avg_delay"] = (
        df["delay_days"].mean() if "delay_days" in df else 0
    )

    result["customer_rating"] = (
        df["customer_rating"].mean()
        if "customer_rating" in df
        else 0
    )

    return result

# ============================================================
# SIDEBAR FILTERS
# ============================================================

def filter_multiselect(df, column, label):
    """Create a sidebar multiselect and filter the dataframe."""
    if column not in df.columns:
        return df

    options = sorted(df[column].dropna().astype(str).unique().tolist())

    selected = st.sidebar.multiselect(label, options)

    if selected:
        return df[df[column].astype(str).isin(selected)]

    return df


def show_sidebar_filters(dataframe):
    """Display dashboard filters and return filtered data."""
    st.sidebar.markdown(
        '<h2 style="font-weight:800;">Dashboard Filters</h2>',
        unsafe_allow_html=True,
    )
    st.sidebar.caption(
        f"Dataset: {len(dataframe):,} rows × {len(dataframe.columns)} columns"
    )

    filtered = dataframe.copy()

    if "order_date" in filtered.columns:
        dates = filtered["order_date"].dropna()

        if not dates.empty:
            min_date = dates.min().date()
            max_date = dates.max().date()

            selected_dates = st.sidebar.date_input(
                "Order Date",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
            )

            if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
                start_date, end_date = selected_dates
                filtered = filtered[
                    (filtered["order_date"].dt.date >= start_date)
                    & (filtered["order_date"].dt.date <= end_date)
                ]

    for column, label in [
        ("warehouse", "Warehouse"),
        ("origin_city", "Origin City"),
        ("destination_city", "Destination City"),
        ("shipping_mode", "Shipping Mode"),
        ("product_category", "Product Category"),
        ("delivery_partner", "Delivery Partner"),
        ("delivery_status", "Delivery Status"),
    ]:
        filtered = filter_multiselect(filtered, column, label)

    return filtered

# ============================================================
# OVERVIEW
# ============================================================

def show_overview(dataframe):
    """Display the executive overview and main KPIs."""
    section_title("Key Performance Indicators")

    kpis = calculate_kpis(dataframe)

    rows = [
        [
            ("Total Orders", format_number(kpis["total_orders"]), "Orders in selection"),
            ("Delivered", format_number(kpis["delivered_orders"]), "Successfully delivered"),
            ("Delayed", format_number(kpis["delayed_orders"]), "Delayed shipments"),
        ],
        [
            ("On-Time Rate", format_percentage(kpis["on_time_rate"]), "On-time delivery rate"),
            ("Avg Delivery", f"{kpis['avg_delivery_days']:.2f} days", "Average delivery duration"),
            ("Avg Cost", format_currency(kpis["avg_cost"]), "Average logistics cost"),
        ],
        [
            ("Total Logistics Cost", format_currency(kpis["total_cost"]), "Total selected logistics cost"),
            ("Avg Delay", f"{kpis['avg_delay']:.2f} days", "Average delay"),
            ("Customer Rating", f"{kpis['customer_rating']:.2f} / 5", "Average customer rating"),
        ],
    ]

    for row in rows:
        columns = st.columns(3)
        for column, card in zip(columns, row):
            with column:
                create_kpi_card(*card)

    section_title("Delivery Status")

    if "delivery_status" in dataframe.columns:
        status = (
            dataframe["delivery_status"]
            .value_counts()
            .rename_axis("Delivery Status")
            .to_frame("Orders")
        )
        st.bar_chart(status, height=300)

    subsection_title("Orders by Warehouse")

    if "warehouse" in dataframe.columns:
        warehouse = dataframe["warehouse"].value_counts().head(10)
        st.bar_chart(warehouse, height=300)

# ============================================================
# DELIVERY ANALYSIS
# ============================================================

def show_delivery_analysis(dataframe):
    """Display delivery performance analysis."""
    section_title("Delivery Analysis")

    col1, col2 = st.columns(2)

    with col1:
        if "delivery_days" in dataframe.columns:
            st.metric(
                "Average Delivery Days",
                f"{dataframe['delivery_days'].mean():.2f}",
            )

    with col2:
        if "delay_days" in dataframe.columns:
            st.metric(
                "Average Delay Days",
                f"{dataframe['delay_days'].mean():.2f}",
            )

    subsection_title("Delivery Status")

    if "delivery_status" in dataframe.columns:
        status = dataframe["delivery_status"].value_counts()
        st.bar_chart(status, height=300)

    subsection_title("Delivery Days Distribution")

    if "delivery_days" in dataframe.columns:
        delivery = dataframe["delivery_days"].dropna()
        bins = pd.cut(delivery, bins=10)
        distribution = bins.value_counts().sort_index()
        distribution.index = distribution.index.astype(str)
        st.bar_chart(distribution, height=300)

    subsection_title("Delivery Performance by Shipping Mode")

    if {"shipping_mode", "on_time_flag"}.issubset(dataframe.columns):
        mode = (
            dataframe.groupby("shipping_mode")["on_time_flag"]
            .mean()
            .mul(100)
            .sort_values(ascending=False)
        )
        st.bar_chart(mode, height=300)

# ============================================================
# ROUTE ANALYSIS
# ============================================================

def show_route_analysis(dataframe):
    """Display route-level order, delivery and cost analysis."""
    section_title("Route Analysis")

    required = {"origin_city", "destination_city"}

    if required.issubset(dataframe.columns):
        route_df = dataframe.copy()
        route_df["route"] = (
            route_df["origin_city"].astype(str)
            + " → "
            + route_df["destination_city"].astype(str)
        )

        subsection_title("Top Routes by Orders")

        route_orders = route_df["route"].value_counts().head(10)
        st.bar_chart(route_orders, height=320)

        if "total_logistics_cost" in route_df.columns:
            subsection_title("Top Routes by Logistics Cost")
            route_cost = (
                route_df.groupby("route")["total_logistics_cost"]
                .sum()
                .sort_values(ascending=False)
                .head(10)
            )
            st.bar_chart(route_cost, height=320)

        if "delivery_days" in route_df.columns:
            subsection_title("Average Delivery Days by Route")
            route_days = (
                route_df.groupby("route")["delivery_days"]
                .mean()
                .sort_values(ascending=False)
                .head(10)
            )
            st.bar_chart(route_days, height=320)
    else:
        st.info("Route columns are not available in the dataset.")

# ============================================================
# WAREHOUSE ANALYSIS
# ============================================================

def show_warehouse_analysis(dataframe):
    """Display warehouse-level performance analysis."""
    section_title("Warehouse Analysis")

    if "warehouse" not in dataframe.columns:
        st.info("Warehouse column is not available.")
        return

    subsection_title("Orders by Warehouse")
    orders = dataframe["warehouse"].value_counts()
    st.bar_chart(orders, height=300)

    if "on_time_flag" in dataframe.columns:
        subsection_title("On-Time Delivery by Warehouse")
        on_time = (
            dataframe.groupby("warehouse")["on_time_flag"]
            .mean()
            .mul(100)
            .sort_values(ascending=False)
        )
        st.bar_chart(on_time, height=300)

    if "delivery_days" in dataframe.columns:
        subsection_title("Average Delivery Days by Warehouse")
        delivery = (
            dataframe.groupby("warehouse")["delivery_days"]
            .mean()
            .sort_values(ascending=False)
        )
        st.bar_chart(delivery, height=300)

    if "total_logistics_cost" in dataframe.columns:
        subsection_title("Logistics Cost by Warehouse")
        cost = (
            dataframe.groupby("warehouse")["total_logistics_cost"]
            .sum()
            .sort_values(ascending=False)
        )
        st.bar_chart(cost, height=300)

# ============================================================
# COST ANALYSIS
# ============================================================

def show_cost_analysis(dataframe):
    """Display logistics cost analysis."""
    section_title("Cost Analysis")

    total_cost = (
        dataframe["total_logistics_cost"].sum()
        if "total_logistics_cost" in dataframe.columns
        else 0
    )

    average_cost = (
        dataframe["total_logistics_cost"].mean()
        if "total_logistics_cost" in dataframe.columns
        else 0
    )

    cost_per_km = (
        dataframe["cost_per_km"].mean()
        if "cost_per_km" in dataframe.columns
        else 0
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Total Logistics Cost", format_currency(total_cost))

    with c2:
        st.metric("Average Cost / Order", format_currency(average_cost))

    with c3:
        st.metric("Average Cost / KM", format_currency(cost_per_km))

    if "shipping_mode" in dataframe.columns and "total_logistics_cost" in dataframe.columns:
        subsection_title("Cost by Shipping Mode")
        mode_cost = (
            dataframe.groupby("shipping_mode")["total_logistics_cost"]
            .sum()
            .sort_values(ascending=False)
        )
        st.bar_chart(mode_cost, height=320)

    if "product_category" in dataframe.columns and "total_logistics_cost" in dataframe.columns:
        subsection_title("Cost by Product Category")
        category_cost = (
            dataframe.groupby("product_category")["total_logistics_cost"]
            .sum()
            .sort_values(ascending=False)
        )
        st.bar_chart(category_cost, height=320)

    if "order_date" in dataframe.columns and "total_logistics_cost" in dataframe.columns:
        subsection_title("Monthly Logistics Cost")
        monthly = (
            dataframe.dropna(subset=["order_date"])
            .set_index("order_date")
            .resample("ME")["total_logistics_cost"]
            .sum()
        )
        st.line_chart(monthly, height=320)

# ============================================================
# PARTNER ANALYSIS
# ============================================================

def show_partner_analysis(dataframe):
    """Display delivery partner performance and cost analysis."""
    section_title("Partner Analysis")

    if "delivery_partner" not in dataframe.columns:
        st.info("Delivery partner column is not available.")
        return

    subsection_title("Orders by Delivery Partner")
    orders = dataframe["delivery_partner"].value_counts()
    st.bar_chart(orders, height=300)

    if "on_time_flag" in dataframe.columns:
        subsection_title("On-Time Delivery by Partner")
        performance = (
            dataframe.groupby("delivery_partner")["on_time_flag"]
            .mean()
            .mul(100)
            .sort_values(ascending=False)
        )
        st.bar_chart(performance, height=300)

    if "total_logistics_cost" in dataframe.columns:
        subsection_title("Logistics Cost by Partner")
        cost = (
            dataframe.groupby("delivery_partner")["total_logistics_cost"]
            .sum()
            .sort_values(ascending=False)
        )
        st.bar_chart(cost, height=300)

    if "customer_rating" in dataframe.columns:
        subsection_title("Customer Rating by Partner")
        rating = (
            dataframe.groupby("delivery_partner")["customer_rating"]
            .mean()
            .sort_values(ascending=False)
        )
        st.bar_chart(rating, height=300)

# ============================================================
# MAIN APPLICATION
# ============================================================

def main():
    """Run the Streamlit dashboard."""
    dataframe = load_dashboard_data()
    filtered_data = show_sidebar_filters(dataframe)

    if filtered_data.empty:
        st.warning(
            "No records match the selected filters. "
            "Please change the filters."
        )
        return

    selected_page = st.radio(
        "Dashboard Section",
        [
            "Executive Overview",
            "Delivery Analysis",
            "Route Analysis",
            "Warehouse Analysis",
            "Cost Analysis",
            "Partner Analysis",
        ],
        horizontal=True,
    )

    st.divider()

    if selected_page == "Executive Overview":
        show_overview(filtered_data)

    elif selected_page == "Delivery Analysis":
        show_delivery_analysis(filtered_data)

    elif selected_page == "Route Analysis":
        show_route_analysis(filtered_data)

    elif selected_page == "Warehouse Analysis":
        show_warehouse_analysis(filtered_data)

    elif selected_page == "Cost Analysis":
        show_cost_analysis(filtered_data)

    elif selected_page == "Partner Analysis":
        show_partner_analysis(filtered_data)


if __name__ == "__main__":
    main()
