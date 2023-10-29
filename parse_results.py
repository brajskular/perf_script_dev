import os
import re
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def parse_args():
    parser = argparse.ArgumentParser(description='parse a folder and search for files whose names start with perf_config')
    parser.add_argument('folder', type=str, help='folder to parse')
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    folder = args.folder

    data = []
    
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.startswith('perf_config'):
                config = re.search('perf_config_(.+)_event_(.*)', file).group(1)
                event = re.search('perf_config_(.+)_event_(.*)', file).group(2)
                unit = ''
                values = []

                with open(os.path.join(root, file), 'r') as f:
                    for line in f:
                        if event in line:
                            newLine = line.replace(',', '')
                            newLine = re.sub('\s+', ',', newLine)
                            lineList = newLine.split(',')
                            value = int(lineList[2].replace(',', ''))
                            unit = lineList[3] if lineList[3] != event else ''

                            values.append(value)

                average = sum(values) / len(values)
                std = np.std(values) / average
                var = np.var(values) / average

                data.append([config, event, average, unit, std, var])

    # Create a DataFrame from the collected data
    columns = ['Config', 'Event', 'Average', 'Unit', 'Normalized_Std', 'Normalized_Var']
    df = pd.DataFrame(data, columns=columns)

    # Print the DataFrame
    print(df)

if __name__ == '__main__':
    main()
