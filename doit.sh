#!/bin/bash
for ((year=1920;year<=2020;year++)); do
	nohup make annotate YEAR=$year PROCESSES_COUNT=2
done
