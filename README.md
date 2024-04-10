# Stock Exchange Server
This is a simple stock exchange server that allows clients to connect and trade stocks. The server is written in Python and uses the `socket` library to communicate with clients. 

## Features
- Clients can connect to the server and trade stocks.
- Using `XML` to communicate between the server and clients.
- The server can handle multiple clients at the same time, using multi-processing with pool.
- Atomic operations are guaranteed by using rollback mechanism and read-write locks.

## How to run
To run the server and testing demo, simply run the following command:
```bash
sudo docker-compose up
```


