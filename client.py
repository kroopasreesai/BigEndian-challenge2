import argparse
import socket
import hashlib
import os
import time

CHUNK_SIZE = 1024


def calculate_hash(filename):
    """Compute SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filename, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            sha256.update(chunk)
    return sha256.hexdigest()


def send_file(client_socket, filename):
    """Send a file to the server with a confirmation mechanism."""
    client_socket.sendall(os.path.basename(filename).encode() + b"\n")

    # Wait for ACK
    ack = client_socket.recv(10).decode().strip()
    if ack != "ACK":
        print("[Client] Server did not acknowledge filename!")
        return False

    with open(filename, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            client_socket.sendall(chunk)
    
    # Send EOF
    client_socket.sendall(b"EOF")
    
    return True


def receive_file(client_socket, save_as):
    """Receive a file from the server and verify integrity."""
    with open(save_as, "wb") as f:
        while True:
            data = client_socket.recv(CHUNK_SIZE)
            if data.endswith(b"EOF"):  # Handle EOF
                f.write(data[:-3])  # Remove 'EOF' marker
                break
            f.write(data)

    # Receive server-side hash
    server_hash = client_socket.recv(64).decode().strip()
    client_hash = calculate_hash(save_as)

    if client_hash == server_hash:
        print("[Client] File integrity verified successfully!")
        return True
    else:
        print("[Client] File corrupted! Requesting retransmission...")
        client_socket.sendall(b"RETRANSMIT")
        return False  # Indicate corruption


def client_main(ip, port, filename):
    """Main client function to upload and receive a file."""
    while True:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))

        print(f"[Client] Uploading {filename}...")
        if not send_file(client_socket, filename):
            print("[Client] Upload failed.")
            client_socket.close()
            return

        print(f"[Client] Receiving file back as received_{filename}...")
        if receive_file(client_socket, f"received_{os.path.basename(filename)}"):
            print("[Client] File transfer successful!")
            client_socket.close()
            break  # Exit loop if file is received correctly
        else:
            print("[Client] Retransmitting due to corruption...")
            time.sleep(1)  # Avoid immediate reconnection loop

    print("[Client] Connection closed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Client File Transfer Client")
    parser.add_argument("-i", "--ip", required=True, help="Server IP")
    parser.add_argument("-p", "--port", type=int, required=True, help="Server Port")
    parser.add_argument("-f", "--file", required=True, help="File to Upload")
    args = parser.parse_args()

    client_main(args.ip, args.port, args.file)
