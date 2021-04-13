#!/usr/bin/python3
import argparse
from pathlib import Path

import matplotlib as plt

import src.visualizers.metric_parser as m_parser


def plot_boxplot():
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Script to parse all the gathered csv \
        metrics into pandas dataframes")

    parser.add_argument(
        "metrics_dir", type=str,
        help="Directory containing the csv files of the metrics")

    parser.add_argument(
        "output_dir", type=str,
        help="Directory to which the visualized metrics will be outputted")

    args = parser.parse_args()

    dir_path = Path(args.metrics_dir)
    if not dir_path.exists():
        print(f"Directory does not exists: ${args.metrics_dir}")
        exit()

    (latency, task, vertex) = m_parser.get_consolidated_dataframes(dir_path)
    df = latency.get_columns(subtask=0, metric="p99")

    pass
