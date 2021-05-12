# Thesis-test-scripts

This repository contains the scripts needed to run 
the evaluation of the dynamic window implementation 
in RMLStreamer against Flink's native window implementation. 


We will call the script from the root folder of this repo. 

# Requirements 
* Java version 1.8
* Make sure rml-streamer repo directory at the same level as this repo's directory 

# Step 1 
Start the docker setup scripts

```
./src/docker_setups.sh 
```
The script will give a prompt for entering super user mode 
to enable writing privileges to Flink in the associated docker volume. 


# Step 2 

Submit a Flink job with a mapping file.

**Note: mapping files used to evaluate thesis could be found under src/resources/mapping_files**

```
./src/job_submitter.sh ...

Usage :  ./src/job_submitter.sh -m mapingfile -o outputPath [options] [--]

    Required: 
    -m|mapping-file     Location of mapping file on the local machine 
    -o|output-path      Location of the output file/folder in the jobmanager's container

    Options:
    -c|compile          Flag to determine if there is a need to compile RMLStreamer 
    -h|help             Display this message
    -v|version          Display script version
``` 



# Step 3 
Start the data generator. 
**Note: you can change the rate of data generated in the script file with the environment 
value "DATA_VOLUME".** 
```
./src/data_generator.sh ... 

Usage :  ./src/data_generator.sh [options] [--]

    Options:
    -m|mode       Stream mode of data generator. Following options are valid:
                  * single-burst 
                  * periodic-burst 
                  * constant-rate (default)

    -h|help       Display this message
    -v|version    Display script version
```

# Step 4 

Start metric gathering scripts. 

```
export PYTHONPATH=$(pwd)
./src/metrics.py


usage: metrics.py [-h] [--interval INTERVAL] [--isTest ISTEST] output maxTimeSeconds

Gather metrics from Flink's web API

positional arguments:
  output               Key of the output file where [output]_subtasks.csv and [output]_mcl.csv will be
                       generated.
  maxTimeSeconds       Maximum time to gather the metrics (should stabilise after a while)

optional arguments:
  -h, --help           show this help message and exit
  --interval INTERVAL  Interval in seconds to gather the metrics from api.
  --isTest ISTEST      Bool flag to check if metrics should be run in test mode.
```


**Repeat Step 1-4 for tumbling window too** 

---

After the metric gather script has finished the job, you could 
visualize the gathered metrics.

# Step 5 

```
export PYTHONPATH=$(pwd)
./src/visualizers/visualizer.py ....


usage: visualizer.py [-h] {constant,periodic} dynamic_metrics_dir tumbling_metrics_dir output_dir

Script to parse all the gathered csv metrics into pandas dataframes and visualize 
them

positional arguments:
  {constant,periodic}   Characteristic of data stream
  dynamic_metrics_dir   Directory containing the csv files of the metrics of a dynamic window
  tumbling_metrics_dir  Directory containing the csv files of the metrics of a tumbling window
  output_dir            Directory to which the visualized metrics will be outputted

optional arguments:
  -h, --help            show this help message and exit
```

