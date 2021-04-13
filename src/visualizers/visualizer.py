import pandas as pd 
import re
import argparse 
import matplotlib as plt


class DFConsolidator(object):

    """Consolidates dataframes if spreaded out in multiple files"""

    def __init__(self, files:list):
        self._frames = [] 
        for f in files: 
            df = pd.read_csv(f)
            self._frames.append(df)

        self._files = files
    
    def clean_headers(self): 
        pass


class LatencyDFs(DFConsolidator):

    def clean_headers(self): 
        for df in self._frames: 
            headers = [re.search("(subtask_index.*)" ,x).group(1) for x in df.columns] 
            df.columns = headers

        

def main():
    files = ["src/resources/dynamic_constant/dynamic_latencies_0.csv"]
    consol = LatencyDFs(files)
    consol.clean_headers()
    print(consol._frames) 

if __name__ == "__main__":
    main()
