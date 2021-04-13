#!/usr/bin/python3
from abc import ABC, abstractmethod
import argparse
from pathlib import Path
import re
from typing import List, Tuple

import pandas as pd
from pandas.core.frame import DataFrame


class DFConsolidator(ABC):

    """Consolidates dataframes if spreaded out in multiple files"""

    @abstractmethod
    def __init__(self, files: List[Path], regex):
        frames = []
        for f in files:
            df = pd.read_csv(f.resolve())
            frames.append(df)

        self.regex = regex
        self._files = files
        cleaned_frames = self._clean_headers(frames)

        self._big_frame = self._consolidate(cleaned_frames)

    @abstractmethod
    def get_columns(self, **kwargs) -> DataFrame:
        pass

    @staticmethod
    def _consolidate(frames: List[DataFrame]) -> DataFrame:

        return pd.concat(frames, axis=1)

    def _clean_headers(self, frames: List[DataFrame]) -> List[DataFrame]:
        for df in frames:
            headers = [re.search(self.regex, col).group(1)
                       for col in df.columns]
            df.columns = headers

        return frames


class LatencyDFs(DFConsolidator):
    def __init__(self, files: List[Path]):
        super().__init__(files, regex="(subtask_index.*)")

    def get_columns(self, **kwargs) -> DataFrame:

        metric = kwargs["metric"]
        subtask = kwargs["subtask"]
        return self._big_frame.filter(
            regex=f"subtask_index\\.{subtask}.*{metric}_",
            axis=1)


class VertexDF(DFConsolidator):
    def __init__(self, files: List[Path]):
        super().__init__(files, regex="\\.(.*)")

    def get_columns(self, **kwargs) -> DataFrame:
        metric = kwargs["metric"]
        return self._big_frame.filter(
            regex=f"{metric}",
            axis=1)


class TaskDF(DFConsolidator):
    def __init__(self, files: List[Path]):
        super().__init__(files, regex="JVM\\.(.*)")

    def get_columns(self, **kwargs) -> DataFrame:
        metric = kwargs["metric"]
        return self._big_frame.filter(
            regex=f"{metric}",
            axis=1)


def get_consolidated_dataframes(directory: Path) \
        -> Tuple[DFConsolidator, DFConsolidator, DFConsolidator]:

    latency_files = list(directory.glob("*latencies*.csv"))
    latency_df = LatencyDFs(latency_files)

    task_file = list(directory.glob("*taskmanager*.csv"))
    task_df = TaskDF(task_file)

    vertex_file = list(directory.glob("*subtask*.csv"))
    vertex_df = VertexDF(vertex_file)

    return (latency_df, task_df, vertex_df)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script to parse all the gathered csv \
        metrics into pandas dataframes")

    parser.add_argument(
        "metrics_dir", type=str,
        help="Directory containing the csv files of the metrics")

    args = parser.parse_args()

    dir_path = Path(args.metrics_dir)
    if not dir_path.exists():
        print(f"Directory does not exists: ${args.metrics_dir}")
        exit()

    get_consolidated_dataframes(dir_path)
