# !/bin/bash
# python3 test.py &
# pid=$!

# echo "Server process started with PID: $pid"
# sleep 1
for i in {1..10}
do
    # python3 client_test_local.py > outcome$i.txt
    python3 client_test_local.py > outcome$i.txt &
    # python3 client.py
done

# kill $pid
# echo "Background process terminated"