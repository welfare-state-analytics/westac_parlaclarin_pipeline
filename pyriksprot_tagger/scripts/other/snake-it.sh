#!/bin/bash
source .env
VERSION=v1.y.z
export OMP_NUM_THREADS=16
for ((year=1920;year<=2020;year++)); do
	echo $year
	nohup make annotate YEAR=$year PROCESSES_COUNT=1 &>> tag.${VERSION}.log
done
