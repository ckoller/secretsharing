#!/bin/bash
#gnome-terminal -x bash -c "celery worker -A celery_worker.celery --loglevel=DEBUG; exec bash"
if [[ $@ -eq null ]]; then
gnome-terminal -x bash -c "python run.py --host=127.0.0.1 --port=5000 --player_count=1 --player_id=1; exec bash"
else
counter=1
port=5000
for ((i=5001; i<=5001+$@-1; i++))
do
gnome-terminal -- bash -c "python run.py --host=127.0.0.1 --port=$i --player_count=$@ --player_id=$counter; exec bash"
let counter=counter+1
let port=$i
sleep 1
done
sleep 2

#curl "http://127.0.0.1:$port/api/commit/?value=5"
#curl "http://127.0.0.1:$port/api/ceps/share/?value=5"
for ((i=5001; i<=5001+$@-1; i++))
do
curl "http://127.0.0.1:$i/ceps_speed"
done
fi