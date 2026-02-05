#!/usr/bin/env python3
\"\"\"
csv_trend_analyzer.py

Parse CSV logs (e.g., test runs or sensor data) and analyze trends.

Expected CSV columns (minimal):
    timestamp, instrument_id, status, value

Example:
    timestamp,instrument_id,status,value
    2025-02-01 10:00:01,IVD-001,PASS,101.3
    2025-02-01 10:05:02,IVD-001,FAIL,98.1

Usage:
    python csv_trend_analyzer.py data.csv --instrument IVD-001

This script:
    - Loads CSV
    - Filters by instrument_id (optional)
    - Computes basic stats and failure rates
    - Plots value vs time and failures over time

Requires:
    - pandas
    - matplotlib
\"\"\"

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def load_csv(path: Path) -> pd.DataFrame:
    \"\"\"Load CSV into a DataFrame and normalize timestamp.\"\"\"
    df = pd.read_csv(path)
    if \"timestamp\" not in df.columns:
        raise ValueError(\"CSV must contain a 'timestamp' column\")

    df[\"timestamp\"] = pd.to_datetime(df[\"timestamp\"], errors=\"coerce\")
    df = df.dropna(subset=[\"timestamp\"])

    return df


def summarize_value(df: pd.DataFrame) -> None:
    \"\"\"Print summary stats for 'value' column.\"\"\"
    if \"value\" not in df.columns:
        print(\"No 'value' column found; skipping numeric summary.\")
        return

    vals = df[\"value\"].dropna()
    print(\"Value statistics:\")
    print(f\"  Count: {vals.count()}\")
    print(f\"  Mean:  {vals.mean():.3f}\")
    print(f\"  Std:   {vals.std():.3f}\")
    print(f\"  Min:   {vals.min():.3f}\")
    print(f\"  Max:   {vals.max():.3f}\")
    print()


def summarize_status(df: pd.DataFrame) -> None:
    \"\"\"Print counts per status (e.g., PASS/FAIL, OK/ERROR).\"\"\"
    if \"status\" not in df.columns:
        print(\"No 'status' column found; skipping status summary.\")
        return

    print(\"Status counts:\")
    print(df[\"status\"].value_counts())
    print()


def plot_value_trend(df: pd.DataFrame, title: str) -> None:
    \"\"\"Plot 'value' over time and its rolling mean.\"\"\"
    if \"value\" not in df.columns:
        return

    df = df.sort_values(\"timestamp\").set_index(\"timestamp\")
    df[\"value_rolling_mean\"] = df[\"value\"].rolling(window=5, min_periods=1).mean()

    plt.figure()
    plt.plot(df.index, df[\"value\"], label=\"Value\")
    plt.plot(df.index, df[\"value_rolling_mean\"], label=\"Rolling mean (5)\")
    plt.xlabel(\"Timestamp\")
    plt.ylabel(\"Value\")
    plt.title(title)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_failure_rate_over_time(df: pd.DataFrame) -> None:
    \"\"\"Plot counts of FAIL (or non-PASS) per day.\"\"\"
    if \"status\" not in df.columns:
        return

    df = df.copy()
    df[\"date\"] = df[\"timestamp\"].dt.date

    # Considering any status that is not 'PASS' as a 'failure' example
    df[\"is_failure\"] = df[\"status\"].ne(\"PASS\")

    daily_failures = df.groupby(\"date\")[\"is_failure\"].sum()

    plt.figure()
    daily_failures.plot(kind=\"bar\")
    plt.xlabel(\"Date\")
    plt.ylabel(\"Failure count\")
    plt.title(\"Failures per day\")
    plt.tight_layout()
    plt.show()


def main() -> None:
    parser = argparse.ArgumentParser(
        description=\"Parse CSV logs and analyze trends.\"
    )
    parser.add_argument(\"csv_file\", type=Path, help=\"Path to CSV file\")
    parser.add_argument(
        \"--instrument\",
        help=\"Optional instrument_id to filter on\",
    )
    args = parser.parse_args()

    df = load_csv(args.csv_file)

    if args.instrument:
        if \"instrument_id\" not in df.columns:
            raise SystemExit(\"No 'instrument_id' column in data to filter on.\")
        df = df[df[\"instrument_id\"] == args.instrument]

    if df.empty:
        raise SystemExit(\"No data after filtering. Check instrument_id.\")

    summarize_value(df)
    summarize_status(df)

    title = \"Value over time\"
    if args.instrument:
        title += f\" (instrument {args.instrument})\"

    plot_value_trend(df, title)
    plot_failure_rate_over_time(df)


if __name__ == \"__main__\":
    main()
