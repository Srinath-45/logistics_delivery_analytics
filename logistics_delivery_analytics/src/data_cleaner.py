"""
Data cleaning and validation functions for the logistics analytics project.
"""

from pathlib import Path

import numpy as np
import pandas as pd


DATE_COLUMNS = [
    "order_date",
    "dispatch_date",
    "expected_delivery_date",
    "actual_delivery_date",
]

NUMERIC_COLUMNS = [
    "distance_km",
    "quantity",
    "weight_kg",
    "shipping_cost",
    "fuel_cost",
    "warehouse_processing_hours",
    "customer_rating",
]

TEXT_COLUMNS = [
    "order_id",
    "customer_id",
    "warehouse",
    "origin_city",
    "destination_city",
    "product_category",
    "shipping_mode",
    "delivery_partner",
    "delivery_status",
    "damage_flag",
    "return_flag",
]


def handle_missing_values(df):
    """Handle missing values according to the logistics data rules."""
    cleaned = df.copy()

    # IDs are required by the business rules.
    cleaned = cleaned.dropna(subset=["order_id", "customer_id"])

    # Fill missing text values with the most common value.
    for column in TEXT_COLUMNS:
        if column in cleaned.columns and cleaned[column].isna().any():
            mode = cleaned[column].mode(dropna=True)

            if not mode.empty:
                cleaned[column] = cleaned[column].fillna(mode.iloc[0])

    # Fill missing numeric values with the median.
    for column in NUMERIC_COLUMNS:
        if column in cleaned.columns and cleaned[column].isna().any():
            median_value = cleaned[column].median()

            if pd.notna(median_value):
                cleaned[column] = cleaned[column].fillna(median_value)

    return cleaned


def remove_duplicates(df):
    """Remove duplicate records from the logistics DataFrame."""
    cleaned = df.copy()

    return cleaned.drop_duplicates().reset_index(drop=True)


def clean_text_columns(df):
    """Clean whitespace and standardize text values."""
    cleaned = df.copy()

    for column in TEXT_COLUMNS:
        if column not in cleaned.columns:
            continue

        cleaned[column] = (
            cleaned[column]
            .astype("string")
            .str.strip()
            .replace("", pd.NA)
        )

    # Standardize common categorical text fields.
    categorical_columns = [
        "warehouse",
        "origin_city",
        "destination_city",
        "product_category",
        "shipping_mode",
        "delivery_partner",
        "delivery_status",
    ]

    for column in categorical_columns:
        if column in cleaned.columns:
            cleaned[column] = cleaned[column].str.title()

    # Normalize Yes/No flag values.
    for column in ["damage_flag", "return_flag"]:
        if column in cleaned.columns:
            cleaned[column] = (
                cleaned[column]
                .str.strip()
                .str.lower()
                .map(
                    {
                        "yes": 1,
                        "no": 0,
                        "1": 1,
                        "0": 0,
                        "true": 1,
                        "false": 0,
                    }
                )
            )

    return cleaned


def clean_date_columns(df):
    """Convert required date columns to Pandas datetime values."""
    cleaned = df.copy()

    for column in DATE_COLUMNS:
        if column in cleaned.columns:
            cleaned[column] = pd.to_datetime(
                cleaned[column],
                errors="coerce",
            )

    return cleaned


def validate_numeric_columns(df):
    """Convert required numeric columns and identify invalid values."""
    cleaned = df.copy()

    for column in NUMERIC_COLUMNS:
        if column in cleaned.columns:
            cleaned[column] = pd.to_numeric(
                cleaned[column],
                errors="coerce",
            )

    return cleaned


def validate_business_rules(df):
    """Validate and remove records that violate defined business rules."""
    cleaned = df.copy()

    # Required identifiers.
    cleaned = cleaned.dropna(
        subset=["order_id", "customer_id"]
    )

    # Distance must be zero or greater.
    if "distance_km" in cleaned.columns:
        cleaned = cleaned[
            cleaned["distance_km"].ge(0)
        ]

    # Quantity must be greater than zero.
    if "quantity" in cleaned.columns:
        cleaned = cleaned[
            cleaned["quantity"].gt(0)
        ]

    # Weight must be zero or greater.
    if "weight_kg" in cleaned.columns:
        cleaned = cleaned[
            cleaned["weight_kg"].ge(0)
        ]

    # Costs must be zero or greater.
    for column in ["shipping_cost", "fuel_cost"]:
        if column in cleaned.columns:
            cleaned = cleaned[
                cleaned[column].ge(0)
            ]

    # Processing hours cannot be negative.
    if "warehouse_processing_hours" in cleaned.columns:
        cleaned = cleaned[
            cleaned["warehouse_processing_hours"].ge(0)
        ]

    # Customer rating must be between 1 and 5.
    if "customer_rating" in cleaned.columns:
        cleaned = cleaned[
            cleaned["customer_rating"].between(1, 5)
        ]

    # Expected delivery should not be before dispatch.
    if {
        "dispatch_date",
        "expected_delivery_date",
    }.issubset(cleaned.columns):

        valid_expected_dates = (
            cleaned["expected_delivery_date"]
            >= cleaned["dispatch_date"]
        )

        cleaned = cleaned[
            valid_expected_dates
            | cleaned["expected_delivery_date"].isna()
            | cleaned["dispatch_date"].isna()
        ]

    # Actual delivery should not be before dispatch.
    if {
        "dispatch_date",
        "actual_delivery_date",
    }.issubset(cleaned.columns):

        valid_actual_dates = (
            cleaned["actual_delivery_date"]
            >= cleaned["dispatch_date"]
        )

        cleaned = cleaned[
            valid_actual_dates
            | cleaned["actual_delivery_date"].isna()
            | cleaned["dispatch_date"].isna()
        ]

    return cleaned.reset_index(drop=True)


def create_derived_columns(df):
    """Create delivery, delay, cost, and on-time performance columns."""
    cleaned = df.copy()

    # Delivery duration:
    # actual delivery date - dispatch date.
    cleaned["delivery_days"] = (
        cleaned["actual_delivery_date"]
        - cleaned["dispatch_date"]
    ).dt.days

    # Delay:
    # actual delivery date - expected delivery date.
    cleaned["delay_days"] = (
        cleaned["actual_delivery_date"]
        - cleaned["expected_delivery_date"]
    ).dt.days

    # Avoid division by zero for cost per kilometre.
    cleaned["cost_per_km"] = np.where(
        cleaned["distance_km"] > 0,
        cleaned["shipping_cost"] / cleaned["distance_km"],
        0.0,
    )

    # Total logistics cost.
    cleaned["total_logistics_cost"] = (
        cleaned["shipping_cost"]
        + cleaned["fuel_cost"]
    )

    # Assignment rule:
    # delay_days <= 0 -> On Time
    # delay_days > 0 -> Delayed
    cleaned["on_time_flag"] = np.where(
        cleaned["delay_days"] > 0,
        0,
        1,
    )

    return cleaned


def clean_data(df):
    """Run the complete logistics data cleaning pipeline."""
    cleaned = df.copy()

    cleaned = handle_missing_values(cleaned)
    cleaned = remove_duplicates(cleaned)
    cleaned = clean_text_columns(cleaned)
    cleaned = clean_date_columns(cleaned)
    cleaned = validate_numeric_columns(cleaned)
    cleaned = handle_missing_values(cleaned)
    cleaned = validate_business_rules(cleaned)
    cleaned = create_derived_columns(cleaned)

    return cleaned


def save_cleaned_data(df, output_path):
    """Save the cleaned logistics DataFrame to a CSV file."""
    output_file = Path(output_path)

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        output_file,
        index=False,
    )