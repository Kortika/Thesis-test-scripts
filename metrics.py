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


async def calc_metrics(api_url, keys, file):
    count = 0
    metrics_param = {"get": keys}
    with open(file, "w") as f:
        writer = csv.writer(f)
        while True:
            metrics_request = requests.get(url=api_url, params=metrics_param)
            metric_response = metrics_request.json()

            if count == 0:
                header = toCSVHeader(metric_response)
                writer.writerow(header)
                count += 1

            writer.writerow(toCSVRow(metric_response))
            await asyncio.sleep(1)

def run_async_loop(url, keys, outputfile): 
    loop=asyncio.get_event_loop()
    task =loop.create_task(
        calc_metrics(url, keys, outputfile))

    loop.call_later(5, task.cancel)

    try:
        loop.run_until_complete(task)
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":

    parser=argparse.ArgumentParser(
        description='Gather metrics from Flink\'s web API')
    parser.add_argument('--interval', type=int, default=5,
                        required=False,
                        help='Interval in seconds to gather the metrics from api. ')
    parser.add_argument('jobid', type=str,
                        help='Flink\'s job id')
    parser.add_argument('vertexid', type=str,
            help='A vertex of the given job identified in [jobid]')

    parser.add_argument('--output', type=str, default="dynamic", required=False,
                help="Key of the  output file where [output]_subtasks.csv and [output]_mcl.csv will be generated.")

    args=parser.parse_args()

    URL="http://localhost:8081/v1"


    subtask_metrics_url=f"{URL}/jobs/{args.jobid}/vertices/{args.vertexid}/subtasks/metrics"

    subtask_metrics_keys=','.join([
            "numRecordsIn",
            "numRecordsOut",
            "numRecordsInPerSecond",
            "numRecordsOutPerSecond"
            ])

    run_async_loop(subtask_metrics_url, subtask_metrics_keys, f"{args.output}_subtasks.csv")

    
    jobmanager_metrics_url = f"{URL}/jobmanager/metrics"
    jobmanager_metrics_keys = ','.join([
            "Status.JVM.CPU.Load", 
            "Status.JVM.Memory.Heap.Used", 
            "Status.JVM.Memory.Heap.Committed",
            "Status.JVM.Memory.Heap.Max"
            ])
    
    run_async_loop(jobmanager_metrics_url, jobmanager_metrics_keys, f"{args.output}_job.csv")



