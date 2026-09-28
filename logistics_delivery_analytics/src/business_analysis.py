from __future__ import annotations

from pathlib import Path

import pandas as pd


# ============================================================
# Configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "logistics_data.csv"
CLEANED_DATA_PATH = PROJECT_ROOT / "data" / "cleaned" / "logistics_cleaned.csv"
REPORT_PATH = PROJECT_ROOT / "reports" / "business_metrics.csv"


# ============================================================
# Data loading
# ============================================================

def load_cleaned_data() -> pd.DataFrame:
    """
    Load the cleaned logistics dataset.

    If the cleaned file does not exist yet, clean the raw dataset
    using the existing data_cleaner module.
    """

    if CLEANED_DATA_PATH.exists():
        return pd.read_csv(CLEANED_DATA_PATH)

    from src.data_loader import load_data
    from src.data_cleaner import clean_data

    df = load_data(str(RAW_DATA_PATH))
    cleaned_df = clean_data(df)

    CLEANED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(CLEANED_DATA_PATH, index=False)

    return cleaned_df


# ============================================================
# KPI calculations
# ============================================================

def calculate_kpis(df: pd.DataFrame) -> dict:
    """Calculate overall logistics KPIs."""

    total_orders = len(df)

    if total_orders == 0:
        return {
            "total_orders": 0,
            "on_time_rate": 0.0,
            "average_delivery_days": 0.0,
            "average_delay_days": 0.0,
            "average_logistics_cost": 0.0,
            "average_customer_rating": 0.0,
            "damage_rate": 0.0,
            "return_rate": 0.0,
        }

    kpis = {
        "total_orders": total_orders,
        "on_time_rate": (
            df["on_time_flag"].mean() * 100
            if "on_time_flag" in df.columns
            else 0.0
        ),
        "average_delivery_days": (
            df["delivery_days"].mean()
            if "delivery_days" in df.columns
            else 0.0
        ),
        "average_delay_days": (
            df["delay_days"].mean()
            if "delay_days" in df.columns
            else 0.0
        ),
        "average_logistics_cost": (
            df["total_logistics_cost"].mean()
            if "total_logistics_cost" in df.columns
            else 0.0
        ),
        "average_customer_rating": (
            df["customer_rating"].mean()
            if "customer_rating" in df.columns
            else 0.0
        ),
        "damage_rate": (
            calculate_yes_rate(df, "damage_flag")
        ),
        "return_rate": (
            calculate_yes_rate(df, "return_flag")
        ),
    }

    return kpis


def calculate_yes_rate(df: pd.DataFrame, column: str) -> float:
    """Calculate percentage of Yes values in a column."""

    if column not in df.columns or len(df) == 0:
        return 0.0

    values = (
        df[column]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    return (values.eq("yes").mean() * 100)


# ============================================================
# Delivery analysis
# ============================================================

def delivery_status_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize delivery status."""

    if "delivery_status" not in df.columns:
        return pd.DataFrame()

    result = (
        df["delivery_status"]
        .value_counts()
        .rename_axis("delivery_status")
        .reset_index(name="orders")
    )

    result["percentage"] = (
        result["orders"] / len(df) * 100
    ).round(2)

    return result


# ============================================================
# Transport partner analysis
# ============================================================

def partner_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze logistics delivery partners."""

    if "delivery_partner" not in df.columns:
        return pd.DataFrame()

    aggregations = {
        "order_count": ("order_id", "count"),
    }

    if "delivery_days" in df.columns:
        aggregations["avg_delivery_days"] = (
            "delivery_days",
            "mean",
        )

    if "delay_days" in df.columns:
        aggregations["avg_delay_days"] = (
            "delay_days",
            "mean",
        )

    if "on_time_flag" in df.columns:
        aggregations["on_time_rate"] = (
            "on_time_flag",
            "mean",
        )

    if "total_logistics_cost" in df.columns:
        aggregations["avg_logistics_cost"] = (
            "total_logistics_cost",
            "mean",
        )

    if "customer_rating" in df.columns:
        aggregations["avg_customer_rating"] = (
            "customer_rating",
            "mean",
        )

    result = (
        df.groupby("delivery_partner")
        .agg(**aggregations)
        .reset_index()
    )

    if "on_time_rate" in result.columns:
        result["on_time_rate"] *= 100

    numeric_columns = result.select_dtypes(
        include="number"
    ).columns

    result[numeric_columns] = result[numeric_columns].round(2)

    return result.sort_values(
        "order_count",
        ascending=False,
    )


# ============================================================
# Transport mode analysis
# ============================================================

def transport_mode_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze performance by transportation mode."""

    if "transport_mode" not in df.columns:
        return pd.DataFrame()

    aggregations = {
        "order_count": ("order_id", "count"),
    }

    if "delivery_days" in df.columns:
        aggregations["avg_delivery_days"] = (
            "delivery_days",
            "mean",
        )

    if "total_logistics_cost" in df.columns:
        aggregations["avg_logistics_cost"] = (
            "total_logistics_cost",
            "mean",
        )

    if "on_time_flag" in df.columns:
        aggregations["on_time_rate"] = (
            "on_time_flag",
            "mean",
        )

    result = (
        df.groupby("transport_mode")
        .agg(**aggregations)
        .reset_index()
    )

    if "on_time_rate" in result.columns:
        result["on_time_rate"] *= 100

    numeric_columns = result.select_dtypes(
        include="number"
    ).columns

    result[numeric_columns] = result[numeric_columns].round(2)

    return result.sort_values(
        "order_count",
        ascending=False,
    )


# ============================================================
# Route analysis
# ============================================================

def route_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze origin-to-destination routes."""

    required_columns = {
        "origin_city",
        "destination_city",
        "order_id",
    }

    if not required_columns.issubset(df.columns):
        return pd.DataFrame()

    aggregations = {
        "order_count": ("order_id", "count"),
    }

    if "distance_km" in df.columns:
        aggregations["avg_distance_km"] = (
            "distance_km",
            "mean",
        )

    if "delivery_days" in df.columns:
        aggregations["avg_delivery_days"] = (
            "delivery_days",
            "mean",
        )

    if "delay_days" in df.columns:
        aggregations["avg_delay_days"] = (
            "delay_days",
            "mean",
        )

    if "total_logistics_cost" in df.columns:
        aggregations["avg_logistics_cost"] = (
            "total_logistics_cost",
            "mean",
        )

    result = (
        df.groupby(
            [
                "origin_city",
                "destination_city",
            ]
        )
        .agg(**aggregations)
        .reset_index()
    )

    numeric_columns = result.select_dtypes(
        include="number"
    ).columns

    result[numeric_columns] = result[numeric_columns].round(2)

    return result.sort_values(
        "order_count",
        ascending=False,
    )


# ============================================================
# Warehouse analysis
# ============================================================

def warehouse_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze warehouse performance."""

    if "warehouse" not in df.columns:
        return pd.DataFrame()

    aggregations = {
        "order_count": ("order_id", "count"),
    }

    if "delivery_days" in df.columns:
        aggregations["avg_delivery_days"] = (
            "delivery_days",
            "mean",
        )

    if "delay_days" in df.columns:
        aggregations["avg_delay_days"] = (
            "delay_days",
            "mean",
        )

    if "on_time_flag" in df.columns:
        aggregations["on_time_rate"] = (
            "on_time_flag",
            "mean",
        )

    if "total_logistics_cost" in df.columns:
        aggregations["avg_logistics_cost"] = (
            "total_logistics_cost",
            "mean",
        )

    result = (
        df.groupby("warehouse")
        .agg(**aggregations)
        .reset_index()
    )

    if "on_time_rate" in result.columns:
        result["on_time_rate"] *= 100

    numeric_columns = result.select_dtypes(
        include="number"
    ).columns

    result[numeric_columns] = result[numeric_columns].round(2)

    return result.sort_values(
        "order_count",
        ascending=False,
    )


# ============================================================
# Product category analysis
# ============================================================

def category_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze logistics performance by product category."""

    if "product_category" not in df.columns:
        return pd.DataFrame()

    aggregations = {
        "order_count": ("order_id", "count"),
    }

    if "quantity" in df.columns:
        aggregations["total_quantity"] = (
            "quantity",
            "sum",
        )

    if "delivery_days" in df.columns:
        aggregations["avg_delivery_days"] = (
            "delivery_days",
            "mean",
        )

    if "total_logistics_cost" in df.columns:
        aggregations["avg_logistics_cost"] = (
            "total_logistics_cost",
            "mean",
        )

    if "customer_rating" in df.columns:
        aggregations["avg_customer_rating"] = (
            "customer_rating",
            "mean",
        )

    result = (
        df.groupby("product_category")
        .agg(**aggregations)
        .reset_index()
    )

    numeric_columns = result.select_dtypes(
        include="number"
    ).columns

    result[numeric_columns] = result[numeric_columns].round(2)

    return result.sort_values(
        "order_count",
        ascending=False,
    )


# ============================================================
# Generate report
# ============================================================

def generate_report(df: pd.DataFrame) -> dict:
    """Generate all business analysis outputs."""

    report = {
        "kpis": calculate_kpis(df),
        "delivery_status": delivery_status_analysis(df),
        "partners": partner_analysis(df),
        "transport_modes": transport_mode_analysis(df),
        "routes": route_analysis(df),
        "warehouses": warehouse_analysis(df),
        "categories": category_analysis(df),
    }

    return report


# ============================================================
# Save KPI report
# ============================================================

def save_kpi_report(kpis: dict) -> None:
    """Save KPI values to CSV."""

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_df = pd.DataFrame(
        [
            {
                "metric": key,
                "value": value,
            }
            for key, value in kpis.items()
        ]
    )

    report_df.to_csv(
        REPORT_PATH,
        index=False,
    )


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("LOGISTICS BUSINESS ANALYSIS")
    print("=" * 60)

    df = load_cleaned_data()

    print(f"\nRows analysed: {len(df):,}")
    print(f"Columns analysed: {len(df.columns)}")

    report = generate_report(df)

    print("\n--- KPI SUMMARY ---")

    for metric, value in report["kpis"].items():
        if "rate" in metric:
            print(f"{metric}: {value:.2f}%")
        elif isinstance(value, float):
            print(f"{metric}: {value:.2f}")
        else:
            print(f"{metric}: {value}")

    print("\n--- DELIVERY STATUS ---")
    print(report["delivery_status"].to_string(index=False))

    print("\n--- DELIVERY PARTNERS ---")
    print(report["partners"].to_string(index=False))

    print("\n--- TRANSPORT MODES ---")
    print(report["transport_modes"].to_string(index=False))

    print("\n--- TOP ROUTES ---")
    print(
        report["routes"]
        .head(10)
        .to_string(index=False)
    )

    print("\n--- WAREHOUSES ---")
    print(report["warehouses"].to_string(index=False))

    print("\n--- PRODUCT CATEGORIES ---")
    print(report["categories"].to_string(index=False))

    save_kpi_report(report["kpis"])

    print("\n" + "=" * 60)
    print(f"KPI report saved to: {REPORT_PATH}")
    print("=" * 60)