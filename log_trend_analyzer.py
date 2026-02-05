#!/usr/bin/env python3
\"\"\"
log_trend_analyzer.py

Parse plain-text log files and extract trends.

Expected log format (one entry per line):

    <timestamp>,<level>,<instrument_id>,<message>

Examples:
    2025-02-01 10:00:01,INFO,IVD-001,pressure_kpa=101.3
    2025-02-01 10:05:02,WARN,IVD-001,pressure_kpa=98.1
    2025-02-01 10:10:15,ERROR,IVD-002,pump_stall

This script:
    - Parses timestamps, levels, instrument_id, and key=value pairs in message
    - Builds a DataFrame
    - Plots a selected metric over time
    - Shows counts of WARN/ERROR per instrument

Usage:
    python log_trend_analyzer.py log.txt --metric pressure_kpa --instrument IVD-001

Requires:
    - pandas
    - matplotlib
\"\"\"

import argparse
import re
from pathlib import Path
from typing import Dict, Optional

import matplotlib.pyplot as plt
import pandas as pd

LOG_PATTERN = re.compile(
    r\"\"\"\n    ^(?P<timestamp>[^,]+),      # timestamp up to first comma\n    (?P<level>[^,]+),           # log level (INFO/WARN/ERROR)\n    (?P<instrument_id>[^,]+),   # instrument id\n    (?P<message>.+)$            # rest of line as message\n    \"\"\",\n    re.VERBOSE,\n)\n\n\ndef parse_message(message: str) -> Dict[str, Optional[float]]:\n    \"\"\"Parse key=value pairs from the message part of the log.\"\"\"\n    result: Dict[str, Optional[float]] = {}\n    if \"=\" not in message:\n        return result\n\n    tokens = re.split(r\"[ ,]+\", message.strip())\n    for token in tokens:\n        if \"=\" in token:\n            key, value_str = token.split(\"=\", 1)\n            try:\n                value = float(value_str)\n            except ValueError:\n                value = None\n            result[key] = value\n\n    return result\n\n\ndef load_log(path: Path) -> pd.DataFrame:\n    \"\"\"Parse a log file into a DataFrame.\"\"\"\n    records = []\n\n    with path.open(\"r\", encoding=\"utf-8\") as f:\n        for line in f:\n            line = line.strip()\n            if not line:\n                continue\n\n            m = LOG_PATTERN.match(line)\n            if not m:\n                continue\n\n            data = m.groupdict()\n            msg_fields = parse_message(data[\"message\"])\n\n            record: Dict[str, Optional[float]] = {\n                \"timestamp\": data[\"timestamp\"],\n                \"level\": data[\"level\"],\n                \"instrument_id\": data[\"instrument_id\"],\n                \"message\": data[\"message\"],\n            }\n            record.update(msg_fields)\n            records.append(record)\n\n    df = pd.DataFrame(records)\n    if df.empty:\n        raise ValueError(\"No valid log lines parsed.\")\n\n    df[\"timestamp\"] = pd.to_datetime(df[\"timestamp\"], errors=\"coerce\")\n    df = df.dropna(subset=[\"timestamp\"])\n\n    return df\n\n\ndef plot_metric(df: pd.DataFrame, metric: str, title: str) -> None:\n    \"\"\"Plot numeric metric over time if present.\"\"\"\n    if metric not in df.columns:\n        print(f\"Metric '{metric}' not found in parsed logs; skipping metric plot.\")\n        return\n\n    metric_df = df.dropna(subset=[metric]).sort_values(\"timestamp\")\n    if metric_df.empty:\n        print(f\"No valid values for metric '{metric}'.\")\n        return\n\n    plt.figure()\n    plt.plot(metric_df[\"timestamp\"], metric_df[metric], label=metric)\n    plt.xlabel(\"Timestamp\")\n    plt.ylabel(metric)\n    plt.title(title)\n    plt.xticks(rotation=45)\n    plt.tight_layout()\n    plt.show()\n\n\ndef plot_error_counts(df: pd.DataFrame) -> None:\n    \"\"\"Plot WARN/ERROR counts per instrument.\"\"\"\n    subset = df[df[\"level\"].isin([\"WARN\", \"ERROR\"])]\n    if subset.empty:\n        print(\"No WARN/ERROR entries found in logs.\")\n        return\n\n    counts = subset[\"instrument_id\"].value_counts()\n\n    plt.figure()\n    counts.plot(kind=\"bar\")\n    plt.xlabel(\"Instrument ID\")\n    plt.ylabel(\"WARN/ERROR count\")\n    plt.title(\"WARN/ERROR count per instrument\")\n    plt.tight_layout()\n    plt.show()\n\n\ndef main() -> None:\n    parser = argparse.ArgumentParser(\n        description=\"Parse plain-text log files and analyze trends.\"\n    )\n    parser.add_argument(\"log_file\", type=Path, help=\"Path to log file\")\n    parser.add_argument(\n        \"--metric\",\n        help=\"Numeric metric key to plot (e.g., pressure_kpa)\",\n    )\n    parser.add_argument(\n        \"--instrument\",\n        help=\"Optional instrument_id to filter on (e.g., IVD-001)\",\n    )\n\n    args = parser.parse_args()\n\n    df = load_log(args.log_file)\n\n    if args.instrument:\n        df = df[df[\"instrument_id\"] == args.instrument]\n\n    if df.empty:\n        raise SystemExit(\"No data after filtering. Check instrument_id or file content.\")\n\n    print(\"Log levels:\")\n    print(df[\"level\"].value_counts())\n    print()\n\n    if args.metric:\n        title = f\"{args.metric} over time\"\n        if args.instrument:\n            title += f\" (instrument {args.instrument})\"\n        plot_metric(df, args.metric, title)\n\n    plot_error_counts(df)\n\n\nif __name__ == \"__main__\":\n    main()\n