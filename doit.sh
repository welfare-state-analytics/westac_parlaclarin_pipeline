#!/bin/bash
for ((year=1982;year<=2020;year++)); do
	nohup make annotate YEAR=$year CPU_COUNT=2
done
