#!/bin/bash

curl -g "http://3.16.28.44/ceps/setup/bool/10/[0,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200]"
curl -g "http://3.16.169.134/ceps/setup/bool/10/[0,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200]"
curl -g "http://3.16.186.27/ceps/setup/bool/10/[0,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200]"
curl -g "http://3.16.206.106/ceps/setup/bool/10/[0,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200]"
curl -g "http://3.16.255.215/ceps/setup/bool/10/[0,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200]"
curl -g "http://3.17.9.108/ceps/setup/bool/10/[0,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200]"
curl -g "http://3.17.11.159/ceps/setup/bool/10/[0,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200]"
curl -g "http://13.58.1.217/ceps/setup/bool/10/[0,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200]"
curl -g "http://18.191.73.63/ceps/setup/bool/10/[0,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200]"
curl -g "http://18.216.10.150/ceps/setup/bool/10/[0,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200,%200]"

sleep 8

curl "http://3.16.28.44/ceps/run/"
curl "http://3.16.28.44/ceps/run/"
curl "http://3.16.186.27/ceps/run/"
curl "http://3.16.206.106/ceps/run/"
curl "http://3.16.255.215/ceps/run/"
curl "http://3.17.9.108/ceps/run/"
curl "http://3.17.11.159/ceps/run/"
curl "http://13.58.1.217/ceps/run/"
curl "http://18.191.73.63/ceps/run/"
curl "http://18.216.10.150/ceps/run/"


