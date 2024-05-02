import socket
import struct
import threading

class ChatServer:
    def __init__(self, host='127.0.0.1', port=12345):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rooms = {}
        self.lock = threading.Lock()

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"Server listening on {self.host}:{self.port}")
        while True:
            client_socket, addr = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket, addr)).start()

    def handle_client(self, client_socket, addr):
        while True:
            try:
                # Receive the header first
                header = client_socket.recv(32)
                if not header:
                    break

                # ヘッダー（32 バイト）: RoomNameSize（1 バイト） | Operation（1 バイト） | State（1 バイト） | OperationPayloadSize（29 バイト）
                room_name_size, operation, state = struct.unpack('B B B', header[:3])
                operation_payload_size = int.from_bytes(header[3:], 'big')

                # Now receive the payload based on the size specified
                payload = client_socket.recv(operation_payload_size)

                if operation == 0:  # Create new room
                    room_name = payload.decode('utf-8')
                    self.create_room(client_socket, room_name, addr)
                elif operation == 1:  # Join room
                    self.join_room(client_socket, payload, addr)

            except Exception as e:
                print(f"Error: {e}")
                break
        client_socket.close()

    def create_room(self, client_socket, room_name, addr):
        token = f"{addr[0]}:{addr[1]}:{room_name}"
        with self.lock:
            self.rooms[token] = {"name": room_name, "host": addr, "clients": {addr}}
        client_socket.sendall(token.encode())

    def join_room(self, client_socket, token, addr):
        with self.lock:
            if token in self.rooms:
                self.rooms[token]['clients'].add(addr)
                client_socket.sendall(b"Joined")
            else:
                client_socket.sendall(b"Invalid token")

if __name__ == "__main__":
    server = ChatServer()
    server.start()
