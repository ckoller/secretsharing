#!/bin/bash

curl -g "http://18.222.137.164/ceps_speed/setup/bool/10/[0,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200]"
curl -g "http://3.16.28.44/ceps_speed/setup/bool/10/[0,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200]"
curl -g "http://18.223.152.184/ceps_speed/setup/bool/10/[0,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200]"


sleep 5

curl "http://18.222.137.164/ceps_speed/run/"
curl "http://3.16.28.44/ceps_speed/run/"
curl "http://18.223.152.184/ceps_speed/run/"