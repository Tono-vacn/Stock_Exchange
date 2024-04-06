#!/bin/bash

# sleep 10

python3 server_init.py &
pid=$!

echo "Server process started with PID: $pid"
sleep 1
for i in {1..10}
do
    python3 ./testing/scalability/client_test_local.py > ./testing/outcome$i.txt &
done

sleep 5

kill $pid
echo "Background process terminated"