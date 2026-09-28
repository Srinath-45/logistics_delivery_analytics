from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# ============================================================
# Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "cleaned"
    / "logistics_cleaned.csv"
)

CHART_DIR = (
    PROJECT_ROOT
    / "reports"
    / "charts"
)


# ============================================================
# Setup
# ============================================================

def load_data() -> pd.DataFrame:
    """Load the cleaned logistics dataset."""

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found: {DATA_PATH}\n"
            "Run the data cleaning step first."
        )

    return pd.read_csv(DATA_PATH)


def setup_chart_directory() -> None:
    """Create the chart output directory."""

    CHART_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


# ============================================================
# Chart 1 - Delivery Status
# ============================================================

def plot_delivery_status(df: pd.DataFrame) -> None:
    """Create delivery-status distribution chart."""

    if "delivery_status" not in df.columns:
        return

    counts = df["delivery_status"].value_counts()

    plt.figure(figsize=(8, 5))

    plt.bar(
        counts.index.astype(str),
        counts.values,
    )

    plt.title("Delivery Status Distribution")
    plt.xlabel("Delivery Status")
    plt.ylabel("Number of Orders")

    plt.xticks(rotation=20)
    plt.tight_layout()

    plt.savefig(
        CHART_DIR / "delivery_status.png",
        dpi=150,
    )

    plt.close()


# ============================================================
# Chart 2 - Orders by Warehouse
# ============================================================

def plot_orders_by_warehouse(df: pd.DataFrame) -> None:
    """Create orders-by-warehouse chart."""

    if "warehouse" not in df.columns:
        return

    counts = (
        df["warehouse"]
        .value_counts()
        .sort_values(ascending=True)
    )

    plt.figure(figsize=(8, 5))

    plt.barh(
        counts.index.astype(str),
        counts.values,
    )

    plt.title("Orders by Warehouse")
    plt.xlabel("Number of Orders")
    plt.ylabel("Warehouse")

    plt.tight_layout()

    plt.savefig(
        CHART_DIR / "orders_by_warehouse.png",
        dpi=150,
    )

    plt.close()


# ============================================================
# Chart 3 - On-Time Rate by Warehouse
# ============================================================

def plot_on_time_by_warehouse(df: pd.DataFrame) -> None:
    """Create warehouse on-time delivery chart."""

    required = {
        "warehouse",
        "on_time_flag",
    }

    if not required.issubset(df.columns):
        return

    result = (
        df.groupby("warehouse")["on_time_flag"]
        .mean()
        .mul(100)
        .sort_values()
    )

    plt.figure(figsize=(8, 5))

    plt.barh(
        result.index.astype(str),
        result.values,
    )

    plt.title("On-Time Delivery Rate by Warehouse")
    plt.xlabel("On-Time Rate (%)")
    plt.ylabel("Warehouse")

    plt.xlim(0, 100)

    plt.tight_layout()

    plt.savefig(
        CHART_DIR / "on_time_by_warehouse.png",
        dpi=150,
    )

    plt.close()


# ============================================================
# Chart 4 - Orders by Transport Mode
# ============================================================

def plot_orders_by_transport_mode(
    df: pd.DataFrame,
) -> None:
    """Create transport-mode order distribution."""

    if "transport_mode" not in df.columns:
        return

    counts = df["transport_mode"].value_counts()

    plt.figure(figsize=(8, 5))

    plt.bar(
        counts.index.astype(str),
        counts.values,
    )

    plt.title("Orders by Transport Mode")
    plt.xlabel("Transport Mode")
    plt.ylabel("Number of Orders")

    plt.xticks(rotation=20)

    plt.tight_layout()

    plt.savefig(
        CHART_DIR / "orders_by_transport_mode.png",
        dpi=150,
    )

    plt.close()


# ============================================================
# Chart 5 - Logistics Cost by Transport Mode
# ============================================================

def plot_cost_by_transport_mode(
    df: pd.DataFrame,
) -> None:
    """Create average logistics cost by transport mode."""

    required = {
        "transport_mode",
        "total_logistics_cost",
    }

    if not required.issubset(df.columns):
        return

    result = (
        df.groupby("transport_mode")[
            "total_logistics_cost"
        ]
        .mean()
        .sort_values(ascending=False)
    )

    plt.figure(figsize=(8, 5))

    plt.bar(
        result.index.astype(str),
        result.values,
    )

    plt.title("Average Logistics Cost by Transport Mode")
    plt.xlabel("Transport Mode")
    plt.ylabel("Average Logistics Cost")

    plt.xticks(rotation=20)

    plt.tight_layout()

    plt.savefig(
        CHART_DIR / "cost_by_transport_mode.png",
        dpi=150,
    )

    plt.close()


# ============================================================
# Chart 6 - Orders by Product Category
# ============================================================

def plot_orders_by_category(
    df: pd.DataFrame,
) -> None:
    """Create product-category order chart."""

    if "product_category" not in df.columns:
        return

    counts = (
        df["product_category"]
        .value_counts()
        .sort_values(ascending=True)
    )

    plt.figure(figsize=(9, 6))

    plt.barh(
        counts.index.astype(str),
        counts.values,
    )

    plt.title("Orders by Product Category")
    plt.xlabel("Number of Orders")
    plt.ylabel("Product Category")

    plt.tight_layout()

    plt.savefig(
        CHART_DIR / "orders_by_category.png",
        dpi=150,
    )

    plt.close()


# ============================================================
# Chart 7 - Average Delivery Days by Category
# ============================================================

def plot_delivery_days_by_category(
    df: pd.DataFrame,
) -> None:
    """Create average delivery time by category chart."""

    required = {
        "product_category",
        "delivery_days",
    }

    if not required.issubset(df.columns):
        return

    result = (
        df.groupby("product_category")["delivery_days"]
        .mean()
        .sort_values()
    )

    plt.figure(figsize=(9, 6))

    plt.barh(
        result.index.astype(str),
        result.values,
    )

    plt.title(
        "Average Delivery Days by Product Category"
    )

    plt.xlabel("Average Delivery Days")
    plt.ylabel("Product Category")

    plt.tight_layout()

    plt.savefig(
        CHART_DIR / "delivery_days_by_category.png",
        dpi=150,
    )

    plt.close()


# ============================================================
# Chart 8 - Top Routes
# ============================================================

def plot_top_routes(
    df: pd.DataFrame,
    top_n: int = 10,
) -> None:
    """Create top origin-to-destination route chart."""

    required = {
        "origin_city",
        "destination_city",
    }

    if not required.issubset(df.columns):
        return

    routes = (
        df.groupby(
            [
                "origin_city",
                "destination_city",
            ]
        )
        .size()
        .reset_index(name="orders")
        .sort_values(
            "orders",
            ascending=False,
        )
        .head(top_n)
    )

    routes["route"] = (
        routes["origin_city"].astype(str)
        + " → "
        + routes["destination_city"].astype(str)
    )

    routes = routes.sort_values("orders")

    plt.figure(figsize=(10, 6))

    plt.barh(
        routes["route"],
        routes["orders"],
    )

    plt.title(
        f"Top {top_n} Logistics Routes"
    )

    plt.xlabel("Number of Orders")
    plt.ylabel("Route")

    plt.tight_layout()

    plt.savefig(
        CHART_DIR / "top_routes.png",
        dpi=150,
    )

    plt.close()


# ============================================================
# Generate all charts
# ============================================================

def generate_all_charts(
    df: pd.DataFrame,
) -> None:
    """Generate every business chart."""

    setup_chart_directory()

    print("Generating charts...")

    plot_delivery_status(df)
    print("✓ Delivery status chart")

    plot_orders_by_warehouse(df)
    print("✓ Orders by warehouse chart")

    plot_on_time_by_warehouse(df)
    print("✓ On-time warehouse chart")

    plot_orders_by_transport_mode(df)
    print("✓ Transport mode chart")

    plot_cost_by_transport_mode(df)
    print("✓ Transport cost chart")

    plot_orders_by_category(df)
    print("✓ Product category chart")

    plot_delivery_days_by_category(df)
    print("✓ Delivery days category chart")

    plot_top_routes(df)
    print("✓ Top routes chart")

    print("\nAll charts generated successfully.")
    print(f"Charts saved to: {CHART_DIR}")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("LOGISTICS VISUALIZATION")
    print("=" * 60)

    df = load_data()

    print(f"\nRows loaded: {len(df):,}")
    print(f"Columns loaded: {len(df.columns)}")

    generate_all_charts(df)

    print("\n" + "=" * 60)
    print("VISUALIZATION COMPLETE")
    print("=" * 60)