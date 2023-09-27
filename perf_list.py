import subprocess
import csv
import re

# Run 'perf list' command and capture the output
command = ['perf', 'list']
output = subprocess.check_output(command, universal_newlines=True)

# strip all spaces and newlines in the output
output = output.replace(' ', '_').replace('\n', '').replace('[', ',').replace(']', '\n')
csv_file = 'perf_events.csv'

# remove OR.*, from the output
output = re.sub(r'OR.*,', ',', output)
output = re.sub(r'_+,', ',', output)
output = re.sub(r'\n(\w+:)', '\n', output)
# append "Event,Description,Collect" to the output
output = 'Event,Description,Collect\n' + output
output = re.sub(r'\n(_+)', '\n', output)
# write the output to a csv file
with open(csv_file, 'w') as f:
    f.write(output)

# add another column to the csv file 'collect' and fill the rows with 'no'
with open(csv_file, 'r') as f:
    reader = csv.reader(f)
    data = list(reader)

with open(csv_file, 'w') as f:
    writer = csv.writer(f)
    for row in data:
        # skip the first row
        if row[0] == 'Event':
            writer.writerow([row[0], row[1], row[2]])
            continue
        writer.writerow([row[0], row[1], 'no'])

print(f'Events have been written to {csv_file}')
