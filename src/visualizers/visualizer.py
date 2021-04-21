#!/usr/bin/python3
import argparse
from enum import Enum
from pathlib import Path
from typing import Any, List

import matplotlib
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


from scipy.interpolate import make_interp_spline, BSpline
import src.visualizers.error as err
import src.visualizers.metric_parser as m_parser
plt.style.use("ggplot")
matplotlib.rcParams['figure.figsize'] = (8, 6)


class TestType(Enum):
    constant = "constant"
    periodic = "periodic"

    def __str__(self) -> str:
        return self.value


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


def draw_lineplot(df: pd.DataFrame,
                  x: List[Any],
                  title: str,
                  xlabel: str,
                  ylabel: str,
                  ax: Axes,
                  ):

    ax.plot(x, df)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.legend(df.columns)
    return ax


def interpolate(df):
    filler_val = df.min()
    df = df.rolling(30).mean().fillna(filler_val)
    df = df.iloc[::4, :]

    new_y = df
    x = np.arange(0, df.shape[0])
    new_x = np.linspace(min(x), max(x), 300)
    spline = make_interp_spline(x, df, k=5)
    new_y = spline(new_x)

    return pd.DataFrame(new_y, columns=df.columns)


def visualize_latency(dyn_latency: m_parser.DFConsolidator,
                      tumb_latency: m_parser.DFConsolidator,
                      output_dir: Path,
                      test_type: TestType):

    metric = "Latency_avg"
    dyn_df = dyn_latency.get_columns(metric=metric)
    tumb_df = tumb_latency.get_columns(metric=metric)

    dyn_df.columns = ["VCTWindow latency (ms)" for _ in dyn_df.columns]
    tumb_df.columns = ["Tumbling latency (ms)" for _ in tumb_df.columns]
    # removing all zero values due to starting metric collection late
    dyn_df = dyn_df.loc[(dyn_df != 0).all(axis=1), :]
    tumb_df = tumb_df.loc[(tumb_df != 0).all(axis=1), :]

    ax = plt.subplot(111)
    draw_boxplot_ax(dyn_df,
                    [""],
                    f"Data stream with {test_type} rate",
                    "VCTWindow",
                    "Latencies (ms)",
                    ax=ax)
    plt.savefig(output_dir.joinpath("VCTWindow_latency_boxplot.png"))
    plt.close()

    ax = plt.subplot(111)
    draw_boxplot_ax(tumb_df,
                    [""],
                    f"Data stream with {test_type} rate",
                    "TumblingWindow",
                    "Latencies (ms)",
                    ax=ax)
    plt.savefig(output_dir.joinpath("TumblingWindow_latency_boxplot.png"))
    plt.close()

    # Line latency plotting
    ax = plt.subplot(111)
    draw_lineplot(dyn_df,
                  np.arange(0, dyn_df.shape[0]),
                  f"Data stream with {test_type} rate",
                  ylabel="Latency (ms)",
                  xlabel="Time period (s)",
                  ax=ax)

    plt.savefig(output_dir.joinpath("VCTWindow_latency_lineplot.png"))
    plt.close()

    ax = plt.subplot(111)
    draw_lineplot(tumb_df,
                  np.arange(0, tumb_df.shape[0]),
                  f"Data stream with {test_type} rate",
                  ylabel="Latency (ms)",
                  xlabel="Time period (s)",
                  ax=ax)

    plt.savefig(output_dir.joinpath("Tumbling_latency_lineplot.png"))
    plt.close()
    pass


def visualize_throughput(dyn_vert: m_parser.DFConsolidator,
                         tumb_vert: m_parser.DFConsolidator,
                         output_dir: Path,
                         test_type: TestType):

    dyn_out_avg = dyn_vert.get_columns(metric="RecordsOutPerSecond_avg")
    tumb_vert_avg = tumb_vert.get_columns(metric="RecordsOutPerSecond_avg")

    throughput_df = pd.concat([dyn_out_avg, tumb_vert_avg], axis=1)
    throughput_df = throughput_df.fillna(0)

    throughput_df.columns = ["VCTWindow", "TumblingWindow"]

    ax = plt.subplot(111)
    ax = draw_lineplot(throughput_df,
                       np.arange(0, throughput_df.shape[0]),
                       f"Data stream with {test_type} rate",
                       ylabel="Throughput (records/s)",
                       xlabel="Time period (s)",
                       ax=ax)

    plt.savefig(output_dir.joinpath("throughput_comparison.png"))
    plt.close()

    pass


def visualize_jvm_stats(dyn_task: m_parser.DFConsolidator,
                        tumb_task: m_parser.DFConsolidator,
                        output_dir: Path,
                        test_type: str):

    dyna_used_avg_df = dyn_task.get_columns(metric="Used_avg")

    dyna_used_avg_df = dyna_used_avg_df.apply(
        lambda row: [format_bytes(x) for x in row])

    tumb_used_avg_df = tumb_task.get_columns(metric="Used_avg")

    tumb_used_avg_df = tumb_used_avg_df.apply(
        lambda row: [format_bytes(x) for x in row])

    dyna_col_df = interpolate(dyna_used_avg_df.filter(regex="\.Heap"))
    tumb_col_df = interpolate(tumb_used_avg_df.filter(regex="\.Heap"))
    dyna_col_df.columns = ["VCTWindow's heap"]
    tumb_col_df.columns = ["Tumbling's heap"]

    merged_df = pd.concat([dyna_col_df,
                           tumb_col_df], axis=1)

    ax = plt.subplot(111)
    ax = draw_lineplot(merged_df,
                       np.arange(0, merged_df.shape[0]),
                       f"Datastream with {test_type} rate",
                       ylabel="Memory (MB)",
                       xlabel="Time",
                       ax=ax,
                       )
    ax.set_xticklabels([])
    plt.savefig(output_dir.joinpath("mem_comparison.png"))

    plt.close()

    ax = plt.subplot(111)
    ax = draw_lineplot(dyna_used_avg_df,
                       np.arange(0, dyna_used_avg_df.shape[0]),
                       f"Datastream with {test_type} rate",
                       ylabel="Memory (MB)",
                       xlabel="Time period (s)",
                       ax=ax,
                       )
    plt.savefig(output_dir.joinpath("mem_usage_dynamic.png"))

    plt.close()

    ax = plt.subplot(111)
    ax = draw_lineplot(tumb_used_avg_df,
                       np.arange(0, tumb_used_avg_df.shape[0]),
                       f"Datastream with {test_type} rate",
                       ylabel="Memory (MB)",
                       xlabel="Time period (s)",
                       ax=ax,
                       )

    plt.savefig(output_dir.joinpath("mem_usage_tumb.png"))
    plt.close()

    dyn_cpu_df = dyn_task.get_columns(metric="CPU.Load_avg")
    tumb_cpu_df = tumb_task.get_columns(metric="CPU.Load_avg")

    cpu_df = pd.concat([dyn_cpu_df, tumb_cpu_df], axis=1)
    cpu_df.columns = ["VCTWindow", "Tumbling"]
    ax = plt.subplot(111)
    ax = draw_lineplot(cpu_df,
                       np.arange(0, cpu_df.shape[0]),
                       f"Datastream with {test_type} rate",
                       ylabel="CPU (percentage)",
                       xlabel="Time period (s)",
                       ax=ax)

    plt.savefig(output_dir.joinpath("cpu_comparison.png"))
    plt.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Script to parse all the gathered csv \
        metrics into pandas dataframes")

    parser.add_argument(
        "test_type", type=TestType,
        choices=list(TestType),
        help="Characteristic of data stream"
    )
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

    visualize_jvm_stats(dyn_task, tumb_task, output_dir, args.test_type)
    visualize_latency(dyn_latency, tumb_latency, output_dir, args.test_type)
    visualize_throughput(dyn_vertex, tumb_vertex, output_dir, args.test_type)

    pass
