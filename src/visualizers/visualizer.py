#!/usr/bin/python3
import argparse
from pathlib import Path
from typing import Any, List

from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import src.visualizers.error as err
import src.visualizers.metric_parser as m_parser

plt.style.use("ggplot")


def format_bytes(size):
    # convert to MB
    power = 2**10
    n = 0

    while n != 2:
        size /= power
        n += 1
    return size


def get_middle_2min_df(df: pd.DataFrame, start=300, end=420) -> pd.DataFrame:

    return df.iloc[start: end]


def draw_boxplot_ax(data: pd.DataFrame,
                    labels: List[str],
                    title: str,
                    xlabel: str,
                    ylabel: str,
                    ax: Axes,
                    color="lightblue"):

    # notch shape box plot
    bplot2 = ax.boxplot(data,
                        notch=True,  # notch shape
                        vert=True,  # vertical box alignment
                        patch_artist=True,  # fill with color
                        labels=labels)  # will be used to label x-ticks
    ax.set_title(title)

    # fill with colors
    if len(data.columns) > 1:
        colors = ['pink', 'lightblue', 'lightgreen']
        for patch, color in zip(bplot2['boxes'], colors):
            patch.set_facecolor(color)
    else:
        patch = bplot2['boxes'][0]
        patch.set_facecolor(color)

    # adding horizontal grid lines
    ax.yaxis.grid(True)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)


def draw_lineplot(used_avg_df: pd.DataFrame,
                  x: List[Any],
                  title: str,
                  xlabel: str,
                  ylabel: str):
    ax = plt.subplot(111)

    ax.plot(x, used_avg_df)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.legend(used_avg_df.columns)
    return ax


def visualize_latency(dyn_latency: m_parser.DFConsolidator,
                      tumb_latency: m_parser.DFConsolidator,
                      output_dir: Path):

    metric = "Latency_avg"
    dyn_df = dyn_latency.get_columns(metric=metric)
    tumb_df = tumb_latency.get_columns(metric=metric)
    dyn_df = dyn_df.loc[(dyn_df != 0).all(axis=1), :]
    tumb_df = tumb_df.loc[(tumb_df != 0).all(axis=1), :]

    ax = plt.subplot(111)
    draw_boxplot_ax(dyn_df,
                    [""],
                    "Data stream with constant rate",
                    "VCTWindow",
                    "Latencies (ms)",
                    ax=ax)
    plt.savefig(output_dir.joinpath("VCTWindow_latency_boxplot.png"))

    plt.close()

    ax = plt.subplot(1, 1, 1)
    draw_boxplot_ax(tumb_df,
                    [""],
                    "Data stream with constant rate",
                    "TumblingWindow",
                    "Latencies (ms)",
                    ax=ax)
    plt.savefig(output_dir.joinpath("TumblingWindow_latency_boxplot.png"))
    plt.close()

    pass


def visualize_jvm_stats(dyn_task: m_parser.DFConsolidator,
                        tumb_task: m_parser.DFConsolidator):

    print(dyn_task._big_frame.columns)
    used_avg_df = dyn_task.get_columns(metric="Used_avg")
    used_max_df = dyn_task.get_columns(metric="Used_max")

    print(np.arange(0, used_avg_df.shape[0]))
    used_avg_df = used_avg_df.apply(
        lambda row: [format_bytes(x) for x in row])
    ax = draw_lineplot(used_avg_df,
                       np.arange(0, used_avg_df.shape[0]),
                       "Datastream with constant rate",
                       ylabel="Memory (MB)",
                       xlabel="Time period (s)")
    plt.savefig(output_dir.joinpath("mem_usage_dynamic.png"))

    plt.close()

    tumb_used_avg_df = tumb_task.get_columns(metric="Used_avg")
    tumb_used_max_df = dyn_task.get_columns(metric="Used_max")

    tumb_used_avg_df = tumb_used_avg_df.apply(
        lambda row: [format_bytes(x) for x in row])
    ax = draw_lineplot(tumb_used_avg_df,
                       np.arange(0, tumb_used_avg_df.shape[0]),
                       "Datastream with constant rate",
                       ylabel="Memory (MB)",
                       xlabel="Time period (s)")

    plt.savefig(output_dir.joinpath("mem_usage_tumb.png"))
    plt.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Script to parse all the gathered csv \
        metrics into pandas dataframes")

    parser.add_argument(
        "dynamic_metrics_dir", type=str,
        help="Directory containing the csv files \
        of the metrics of a dynamic window")

    parser.add_argument(
        "tumbling_metrics_dir", type=str,
        help="Directory containing the csv files \
        of the metrics of a tumbling window")

    parser.add_argument(
        "output_dir", type=str,
        help="Directory to which the visualized metrics will be outputted")

    args = parser.parse_args()

    dynamic_dir = Path(args.dynamic_metrics_dir)
    tumbling_dir = Path(args.tumbling_metrics_dir)
    output_dir = Path(args.output_dir)

    err.check_directory_exists(output_dir, "Visualization output")
    err.check_directory_exists(dynamic_dir, "Dynamic metrics")
    err.check_directory_exists(tumbling_dir, "Tumbling metrics")

    (dyn_latency, dyn_task, dyn_vertex) = m_parser \
        .get_consolidated_dataframes(dynamic_dir)
    (tumb_latency, tumb_task, tumb_vertex) = m_parser \
        .get_consolidated_dataframes(tumbling_dir)

    visualize_jvm_stats(dyn_task, tumb_task)
    visualize_latency(dyn_latency, tumb_latency, output_dir)

    pass
