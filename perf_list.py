import subprocess
import csv
import re

# Run 'perf list' command and capture the output
command = ['perf', 'list']
output = subprocess.check_output(command, universal_newlines=True)

# strip all spaces and newlines in the output
output = output.replace(' ', '').replace('\n', '').replace('[', ',').replace(']', '\n')
csv_file = 'perf_events.csv'

# remove OR.*, from the output
output = re.sub(r'OR.*,', ',', output)
output = re.sub(r'\n(\w+:)', '\n', output)
# write the output to a csv file
with open(csv_file, 'w') as f:
    f.write(output)

# add another column to the csv file 'collect' and fill the rows with 'no'
with open(csv_file, 'r') as f:
    reader = csv.reader(f)
    data = list(reader)

with open(csv_file, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['Event', 'Description', 'Collect'])
    for row in data:
        writer.writerow([row[0], row[1], 'no'])

print(f'Events have been written to {csv_file}')
