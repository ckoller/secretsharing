#!/bin/bash
# args:     number of servers to create, player_count, circuit type
counter=2
port=5000
for ((i=5002; i<=5002+$1-1; i++))
do
gnome-terminal -- bash -c "python run.py --host=127.0.0.1 --port=$i --player_count=$2 --player_id=$counter --type=$3; exec bash"
let counter=counter+1
let port=$i
sleep 1
done
