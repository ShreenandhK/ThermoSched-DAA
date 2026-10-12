"""ThermoSched command-line entry point.

    python main.py                                  # both scenarios + experiments + dashboard data
    python main.py --scenario scenarios/peak_hours.json   # explain one scenario only
"""

import argparse
import csv
import glob
import json
import os

from thermosched.experiments import run_all
from thermosched.framework import format_report, run_scenario
from thermosched.models import load_scenario

ROOT = os.path.dirname(os.path.abspath(__file__))


def save_csv(name, rows):
    path = os.path.join(ROOT, "results", f"{name}.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return path


def export_dashboard(reports, experiments):
    """Write dashboard/data.js so dashboard/index.html works by double-clicking (no server needed)."""
    data = {"scenarios": reports, "experiments": experiments}
    os.makedirs(os.path.join(ROOT, "dashboard"), exist_ok=True)
    path = os.path.join(ROOT, "dashboard", "data.js")
    with open(path, "w", encoding="utf-8") as f:
        f.write("window.THERMO_DATA = " + json.dumps(data, indent=1, default=str) + ";\n")
    return path


def main():
    parser = argparse.ArgumentParser(description="ThermoSched - thermal-aware CPU workload optimization")
    parser.add_argument("--scenario", help="run only this scenario file")
    args = parser.parse_args()

    if args.scenario:
        print(format_report(run_scenario(load_scenario(args.scenario))))
        return

    reports = []
    for path in sorted(glob.glob(os.path.join(ROOT, "scenarios", "*.json"))):
        report = run_scenario(load_scenario(path))
        print(format_report(report), "\n")
        reports.append(report)

    print("Running experiments (about half a minute)...")
    experiments = run_all()
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    for name, rows in experiments.items():
        print("  saved", os.path.relpath(save_csv(name, rows), ROOT))
    print("  saved", os.path.relpath(export_dashboard(reports, experiments), ROOT))
    print("\nOpen dashboard/index.html in a browser to see the results.")


if __name__ == "__main__":
    main()
