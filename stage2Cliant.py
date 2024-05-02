import socket
import struct
import sys

def create_room(server_ip, server_port, room_name):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((server_ip, server_port))
        # ルーム名のエンコード
        room_name_encoded = room_name.encode('utf-8')
        # ヘッダーの構築
        header = struct.pack('B B B', len(room_name_encoded), 0, 0) + (len(room_name_encoded)).to_bytes(29, 'big')
        sock.sendall(header + room_name_encoded)  # ボディ: 最初の RoomNameSize バイトがルーム名で、その後に OperationPayloadSize バイトが続きます。
        response = sock.recv(4096)
        print(f"Received token: {response.decode()}")

def join_room(server_ip, server_port, token):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((server_ip, server_port))
        # トークンのエンコード
        token_encoded = token.encode('utf-8')
        # ヘッダーの構築
        header = struct.pack('B B B', len(token_encoded), 1, 0) + (len(token_encoded)).to_bytes(29, 'big')
        sock.sendall(header + token_encoded)  # ボディ: 最初の RoomNameSize バイトがルーム名で、その後に OperationPayloadSize バイトが続きます。
        response = sock.recv(4096)
        print(f"Received response: {response.decode()}")

if __name__ == "__main__":
    action = sys.argv[1]
    server_ip = '127.0.0.1'
    server_port = 12345

    if action == "create":
        room_name = sys.argv[2]
        create_room(server_ip, server_port, room_name)
    elif action == "join":
        token = sys.argv[2]
        join_room(server_ip, server_port, token)
