#!/bin/bash


sleep 2

curl -g "http://127.0.0.1:5001/ceps_speed/setup/bool/10/[0,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200]"
curl -g "http://127.0.0.1:5002/ceps_speed/setup/bool/10/[0,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200]"
curl -g "http://127.0.0.1:5003/ceps_speed/setup/bool/10/[0,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200]"

sleep 2

curl "http://127.0.0.1:5001/ceps_speed/run/"
curl "http://127.0.0.1:5002/ceps_speed/run/"
curl "http://127.0.0.1:5003/ceps_speed/run/"
