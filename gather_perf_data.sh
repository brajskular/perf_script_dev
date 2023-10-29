#!/bin/bash

# Check if the binary folder, mav0 location, and counter file arguments are provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <binary_folder> <mav0_location> <counter_file>"
    exit 1
fi

# Assign the script arguments to variables
binary_folder="$1"
mav0_location="$2"
counter_file="$3"

# Check if the counter file exists
if [ ! -f "$counter_file" ]; then
    echo "Counter file not found: $counter_file"
    exit 1
fi

# counter_file is a csv file with the following columns:
# Event,Description,Collect
# branch-instructions,Hardwareevent,yes
# branch-misses,Hardwareevent,yes
# cache-misses,Hardwareevent,no
# cache-references,Hardwareevent,no
# parse this file to get the list of perf events to collect
perf_events=()
while IFS=, read -r event description collect; do
    # print each line
    # echo "event: $event, description: $description, collect: $collect"
    # strip \n from the collect variable
    collect="${collect//[$'\t\r\n ']}"
    if [ "$collect" = "yes" ]; then
        echo "adding event: $event"
        perf_events+=("$event")
    fi
done < "$counter_file"

# print the list of perf events
echo "perf events: ${perf_events[@]}"

# Define the list of plugin configurations
plugin_configs=(
    "offline_cam,offline_imu,pose_prediction"
    "offline_cam,offline_imu,pose_lookup"
)

# Loop through each plugin configuration and perf events
for config in "${plugin_configs[@]}"; do
    for event in "${perf_events[@]}"; do
        echo "Running perf for configuration: $config and event: $event"
        
        # Replace commas with underscores to construct the output suffix
        output_suffix="${config//,/_}"
        
        # Remove the "offline_cam_offline_" prefix from the output suffix
        output_suffix="${output_suffix#offline_cam_offline_imu_}"
        
        # Run taskset and perf in parallel using a subshell
        (
            # Run taskset in the background
            taskset -a -c 9,10,11,12 "$binary_folder/main.opt.exe" -p "$config" --"data=$mav0_location" &
            
            # Capture the taskset process ID
            taskset_pid=$!
            
            # Run perf stat at the same time
            perf stat -D 20000 -I 3000 -C 9,10,11,12 -o "perf_config_${output_suffix}_event_${event}" -e "$event" --interval-count 15 
            
            # Wait for taskset to complete
            wait "$taskset_pid"
        ) &
        
        # Capture the subshell process ID
        subshell_pid=$!
        
        # Wait for the subshell to complete
        wait "$subshell_pid"
        
        echo "Finished perf for configuration: $config and event: $event"
    done
done
