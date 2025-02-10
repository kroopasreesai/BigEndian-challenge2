# BigEndian-challenge2
Multi-Client Client-Server Architecture

This project implements a multi-client client-server architecture using Python. The server can handle multiple clients simultaneously and facilitate communication between them.

Features
Supports multiple clients connecting to the server.
Clients can send and receive messages asynchronously.
Uses sockets for communication.
Concurrent handling of multiple clients using threading.


Execution Instructions

Start the server
python server.py -p 8080

Run multiple clients in different terminals
python client.py -i 127.0.0.1 -p 8080 -f sample1.txt
python client.py -i 127.0.0.1 -p 8080 -f sample2.txt
