import argparse
import socket
import threading
import hashlib
import os
import random
import time

CHUNK_SIZE = 1024
PACKET_LOSS_PROBABILITY = 0.5
DATA_DIR = "server_data"

# Ensure directory exists
os.makedirs(DATA_DIR, exist_ok=True)


def calculate_hash(filename):
    """Calculate SHA-256 hash of a file for integrity verification."""
    sha256 = hashlib.sha256()
    with open(filename, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            sha256.update(chunk)
    return sha256.hexdigest()


def handle_client(client_socket, address):
    """Handles file upload and retransmission to the client."""
    print(f"[Server] Connected to {address}")

    try:
        # Receive filename
        filename = client_socket.recv(CHUNK_SIZE).decode().strip()
        if not filename:
            return
        
        full_path = os.path.join(DATA_DIR, filename)
        
        # Send ACK for filename
        client_socket.sendall(b"ACK")

        # Receive file data
        with open(full_path, "wb") as f:
            while True:
                data = client_socket.recv(CHUNK_SIZE)
                if data.endswith(b"EOF"):  # Handle EOF
                    f.write(data[:-3])  # Remove EOF marker
                    break
                f.write(data)

        print(f"[Server] File '{filename}' received successfully from {address}")

        # Compute file hash
        server_hash = calculate_hash(full_path)

        # Send back the file
        print(f"[Server] Sending back '{filename}' to {address}...")
        
        with open(full_path, "rb") as f:
            while chunk := f.read(CHUNK_SIZE):
                if random.random() > PACKET_LOSS_PROBABILITY:  # Simulate packet loss
                    client_socket.sendall(chunk)
                else:
                    print(f"[Server] Simulating packet loss for {filename}...")
                    time.sleep(0.1)  # Simulating retransmission delay

        client_socket.sendall(b"EOF")

        # Send hash for integrity check
        client_socket.sendall(server_hash.encode())

        # Handle retransmission requests
        retransmission_requested = client_socket.recv(12).decode().strip()
        if retransmission_requested == "RETRANSMIT":
            print(f"[Server] Retransmitting '{filename}' to {address}...")
            handle_client(client_socket, address)  # Recursive retransmission

    except Exception as e:
        print(f"[Server] Error with {address}: {e}")

    finally:
        client_socket.close()
        print(f"[Server] Connection closed for {address}")


def start_server(port):
    """Main server function to handle multiple clients."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", port))
    server_socket.listen(5)
    print(f"[Server] Listening on port {port}")

    while True:
        client_socket, addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Client File Transfer Server")
    parser.add_argument("-p", "--port", type=int, required=True, help="Server Port")
    args = parser.parse_args()

    start_server(args.port)
