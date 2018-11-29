# secretsharing


Install: 

1. pip3 freeze > requirements.txt
2. pip3 install -r requiremtents.txt 

Amazon EC2 servers:

ssh -i "koller.pem" ubuntu@ec2-18-222-137-164.us-east-2.compute.amazonaws.com
ssh -i "koller.pem" ubuntu@ec2-3-16-28-44.us-east-2.compute.amazonaws.com
ssh -i "koller.pem" ubuntu@ec2-18-223-152-184.us-east-2.compute.amazonaws.com

Run:

note:
circuit path in tests/circuits.py is hard coded.
setup in run.py is hardcoded
 
1. sudo python3 run.py &

Shutdown:

1. find PID with htop
2. kill PID

  
