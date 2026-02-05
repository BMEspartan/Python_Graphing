#!/usr/bin/env python3
\"\"\"
json_trend_analyzer.py

Parse JSON measurement logs and generate simple trend plots.

Expected JSON format (list of objects):

[
  {
    "timestamp": "2025-02-01T10:00:01",
    "instrument_id": "IVD-001",
    "metric": "pressure_kpa",
    "value": 101.3
  },
  ...
]

Usage:
    python json_trend_analyzer.py data.json --metric pressure_kpa --instrument IVD-001

Requires:
    - pandas
    - matplotlib
\"\"\"

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def load_json(path: Path) -> pd.DataFrame:
    \"\"\"Load JSON file into a pandas DataFrame.\"\"\"
    with path.open(\"r\", encoding=\"utf-8\") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    if \"timestamp\" not in df.columns:
        raise ValueError(\"JSON must contain a 'timestamp' field\")

    df[\"timestamp\"] = pd.to_datetime(df[\"timestamp\"], errors=\"coerce\")
    df = df.dropna(subset=[\"timestamp\"])

    return df


def summarize(df: pd.DataFrame, metric: str) -> None:
    \"\"\"Print basic statistics for the selected metric.\"\"\"
    if metric not in df.columns:
        raise ValueError(f\"Metric '{metric}' not found in data\")

    series = df[metric].dropna()
    print(f\"Metric: {metric}\")
    print(f\"Count:  {series.count()}\")
    print(f\"Mean:   {series.mean():.3f}\")
    print(f\"Std:    {series.std():.3f}\")
    print(f\"Min:    {series.min():.3f}\")
    print(f\"Max:    {series.max():.3f}\")
    print()


def plot_time_series(df: pd.DataFrame, metric: str, title: str) -> None:
    \"\"\"Plot raw time series and a rolling mean to highlight trends.\"\"\"
    df = df.sort_values(\"timestamp\").set_index(\"timestamp\")

    # Rolling mean to smooth noise (adjust window as needed)
    df[f\"{metric}_roll_mean\"] = df[metric].rolling(window=5, min_periods=1).mean()

    plt.figure()
    plt.plot(df.index, df[metric], label=\"Raw\")
    plt.plot(df.index, df[f\"{metric}_roll_mean\"], label=\"Rolling mean (5)\")

    plt.xlabel(\"Timestamp\")
    plt.ylabel(metric)
    plt.title(title)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def main() -> None:
    parser = argparse.ArgumentParser(
        description=\"Parse JSON measurement logs and plot trends.\"
    )
    parser.add_argument(\"json_file\", type=Path, help=\"Path to JSON file\")
    parser.add_argument(
        \"--metric\",
        required=True,
        help=\"Name of numeric metric field to analyze (e.g., pressure_kpa)\",
    )
    parser.add_argument(
        \"--instrument\",
        help=\"Optional instrument_id to filter on (e.g., IVD-001)\",
    )

    args = parser.parse_args()

    df = load_json(args.json_file)

    if args.instrument:
        if \"instrument_id\" not in df.columns:
            raise SystemExit(\"No 'instrument_id' column in data to filter on.\")
        df = df[df[\"instrument_id\"] == args.instrument]

    if df.empty:
        raise SystemExit(\"No data after filtering. Check metric/instrument names.\")

    summarize(df, args.metric)
    title = f\"{args.metric} over time\"
    if args.instrument:
        title += f\" (instrument {args.instrument})\"

    plot_time_series(df, args.metric, title)


if __name__ == \"__main__\":
    main()
