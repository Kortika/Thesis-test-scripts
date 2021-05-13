#!/usr/bin/python3

import requests
import argparse
import asyncio
import csv


def toCSVHeader(json_arr) -> list:
    header = []
    for metric in json_arr:
        currhead = metric["id"]
        for subval in metric.keys():
            if subval != "id":
                header.append(f"{currhead}_{subval}")

    return header


def toCSVRow(json_arr) -> list:
    values = []
    for metric in json_arr:
        for subval in metric.keys():
            if subval != "id":
                values.append(metric[subval])
    return values


async def calc_metrics(api_url, keys, file, interval=1, header=None):
    count = 0
    metrics_param = {"get": keys}
    with open(file, "w") as f:
        writer = csv.writer(f)
        while True:
            metrics_request = requests.get(url=api_url, params=metrics_param)
            metric_response = metrics_request.json()

            if count == 0:
                if header is None:
                    header = toCSVHeader(metric_response)
                writer.writerow(header)
                count += 1

            writer.writerow(toCSVRow(metric_response))
            f.flush()
            await asyncio.sleep(interval)


def get_vertex_id_name(url, pattern="Window"):
    response = requests.get(url=url).json()

    for vertex in response["vertices"]:
        if pattern in vertex["name"]:
            return (vertex["id"], vertex["name"])
    return None


def get_job_id(url, status):

    response = requests.get(url=url).json()

    for job in response["jobs"]:
        if job["status"] == status:
            return job["id"]
    return None


def get_metrics_id(url, pattern):
    response = requests.get(url=url).json()
    result = []
    for met_id in response:
        if pattern in met_id["id"]:
            result.append(met_id["id"])

    return result


def run_async_loop(aysnc_calls: list, time_seconds: int = 20):
    loop = asyncio.get_event_loop()
    for cal in async_calls:
        task = loop.create_task(cal)
        loop.call_later(time_seconds, task.cancel)

    try:
        loop.run_until_complete(task)
    except asyncio.CancelledError:
        pass


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Gather metrics from Flink\'s web API')
    parser.add_argument('--interval', type=float, default=0.1,
                        required=False,
                        help='Interval in seconds to gather the metrics from api. ')
    parser.add_argument('output', type=str,
                        help="Key of the  output file where [output]_subtasks.csv and [output]_mcl.csv will be generated.")

    parser.add_argument('--isTest', type=bool, default=False, required=False,
                        help="Bool flag to check if metrics should be run in test mode.")

    parser.add_argument('maxTimeSeconds', type=int,
                        help='Maximum time to gather the metrics (should stabilise after a while)')

    args = parser.parse_args()
    BASE_URL = "http://localhost:8081/v1"

    URL = f"{BASE_URL}/jobs"

    STATUS = "CANCELED" if args.isTest else "RUNNING"
    jobid = get_job_id(URL, STATUS)
    URL = f"{URL}/{jobid}"
    vertexid, vertexname = get_vertex_id_name(URL)

    subtask_metrics_url = f"{URL}/vertices/{vertexid}/subtasks/metrics"

    subtask_metrics_keys = ','.join(
        get_metrics_id(subtask_metrics_url, "Window"))

    taskmanagers_metrics_url = f"{BASE_URL}/taskmanagers/metrics"
    taskmanagers_metrics_keys = ','.join([
        "Status.JVM.GarbageCollector.G1_Young_Generation.Count",
        "Status.JVM.CPU.Load",
        "Status.JVM.Memory.Heap.Used",
        "Status.JVM.Memory.Heap.Committed",
        "Status.JVM.Memory.Heap.Max",
        "Status.JVM.Memory.NonHeap.Used",
        "Status.JVM.Memory.NonHeap.Committed",
        "Status.JVM.Memory.NonHeap.Max"
    ])

    latency_metrics_url = f"{URL}/vertices/{vertexid}/subtasks/metrics"
    latency_metrics_keys = ','.join(
        get_metrics_id(latency_metrics_url, "Latency"))

    print(get_metrics_id(latency_metrics_url, "Latency"))
    print(get_metrics_id(taskmanagers_metrics_url, "Status"))
    print(get_metrics_id(subtask_metrics_url, "Window"))

    async_calls = []
    if len(latency_metrics_keys.split(',')) > 20:
        latency_metrics_keys = latency_metrics_keys.split(',')
        count = 0
        for chunk in chunks(latency_metrics_keys, 10):
            async_calls.append(calc_metrics(latency_metrics_url, ','.join(chunk),
                                            f"{args.output}_latencies_{count}.csv", args.interval))
            count += 1

    else:
        async_calls.append(calc_metrics(latency_metrics_url, latency_metrics_keys,
                           f"{args.output}_latencies.csv", args.interval))

    async_calls.append(calc_metrics(
        subtask_metrics_url, subtask_metrics_keys, f"{args.output}_subtasks.csv", args.interval))
    async_calls.append(calc_metrics(taskmanagers_metrics_url,
                       taskmanagers_metrics_keys, f"{args.output}_taskmanager.csv", args.interval))

    run_async_loop(async_calls, args.maxTimeSeconds)
