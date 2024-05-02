import socket
import struct
import sys
import json

def create_room(server_ip, server_port, username):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((server_ip, server_port))
        username_encoded = username.encode('utf-8')
        header = struct.pack('B B B', len(username_encoded), 1, 0) + (len(username_encoded)).to_bytes(29, 'big')
        sock.sendall(header + username_encoded)
        received_data = sock.recv(4096).decode()
        print(f"Received data: {received_data}")
        if received_data:
            response = json.loads(received_data)
            print(f"Room created. Token: {response['token']}")
            return response['token']
        else:
            print("No response received from server or response is empty.")
            return None



def join_room(server_ip, server_port, token):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((server_ip, server_port))
        token_encoded = token.encode('utf-8')
        header = struct.pack('B B B', len(token_encoded), 2, 0) + (len(token_encoded)).to_bytes(29, 'big')
        sock.sendall(header + token_encoded)
        received_data = sock.recv(4096).decode()  # データ受信
        print(f"Received data: {received_data}")  # 受信データのデバッグ出力
        response = json.loads(received_data)  # JSON解析
        print(f"Received response: {response['message']}")
        return response['status'] == 2


def send_udp_message(server_ip, server_port, room_name, token, message):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
        room_name_encoded = room_name.encode('utf-8')
        token_encoded = token.encode('utf-8')
        room_name_size = len(room_name_encoded)
        token_size = len(token_encoded)
        header = struct.pack('B B', room_name_size, token_size)
        packet = header + room_name_encoded + token_encoded + message.encode('utf-8')
        udp_sock.sendto(packet, (server_ip, server_port))

if __name__ == "__main__":
    server_ip = '127.0.0.1'
    server_port_tcp = 12345
    server_port_udp = 12346

    if len(sys.argv) < 3:
        print("Usage: python client.py <action> <username or token> [<message>]")
        sys.exit(1)

    action = sys.argv[1]

    if action == "create":
        username = sys.argv[2]
        token = create_room(server_ip, server_port_tcp, username)
        print("Use the following token to join the chat room:", token)
    elif action == "join":
        token = sys.argv[2]
        if join_room(server_ip, server_port_tcp, token):
            print("Joined the chat room successfully.")
            if len(sys.argv) > 3:
                message = sys.argv[3]
                send_udp_message(server_ip, server_port_udp, "MyRoom", token, message)
                print("Message sent via UDP.")


# import socket
# import struct
# import sys
# import json

# def create_room(server_ip, server_port, username):
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
#         sock.connect((server_ip, server_port))
#         username_encoded = username.encode('utf-8')
#         header = struct.pack('B B B', len(username_encoded), 1, 0) + (len(username_encoded)).to_bytes(29, 'big')
#         sock.sendall(header + username_encoded)  # ユーザー名を含むペイロードを送信
#         response = json.loads(sock.recv(4096).decode())
#         print(f"Room created. Token: {response['token']}")  # トークン受信確認

# def join_room(server_ip, server_port, token):
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
#         sock.connect((server_ip, server_port))
#         token_encoded = token.encode('utf-8')
#         header = struct.pack('B B B', len(token_encoded), 2, 0) + (len(token_encoded)).to_bytes(29, 'big')
#         sock.sendall(header + token_encoded)  # トークンを含むペイロードを送信
#         response = json.loads(sock.recv(4096).decode())
#         print(f"Received response: {response['message']}")  # サーバーからの応答を確認

# if __name__ == "__main__":
#     if len(sys.argv) < 3:
#         print("Usage: python <script> <action> <username or token>")
#         sys.exit(1)
    
#     action = sys.argv[1]
#     server_ip = '127.0.0.1'
#     server_port = 12345

#     if action == "create":
#         username = sys.argv[2]
#         create_room(server_ip, server_port, username)
#     elif action == "join":
#         token = sys.argv[2]
#         join_room(server_ip, server_port, token)



# import socket
# import struct
# import sys
# import json

# def create_room(server_ip, server_port, username):
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
#         sock.connect((server_ip, server_port))
#         username_encoded = username.encode('utf-8')
#         # ヘッダー構築：RoomNameSize | Operation | State | OperationPayloadSize
#         header = struct.pack('B B B', len(username_encoded), 1, 0) + (len(username_encoded)).to_bytes(29, 'big')
#         sock.sendall(header + username_encoded)  # ペイロードには希望するユーザー名が含まれます
#         response = json.loads(sock.recv(4096).decode())
#         if response['status'] == 1:
#             print(f"Room created. Token: {response['token']}")  # サーバからのトークン受信

# def join_room(server_ip, server_port, token):
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
#         sock.connect((server_ip, server_port))
#         token_encoded = token.encode('utf-8')
#         # ヘッダー構築：TokenSize | Operation | State | OperationPayloadSize
#         header = struct.pack('B B B', len(token_encoded), 2, 0) + (len(token_encoded)).to_bytes(29, 'big')
#         sock.sendall(header + token_encoded)  # トークンでチャットルームに参加
#         response = sock.recv(4096).decode()
#         print(f"Received response: {response}")  # サーバからの応答受信

# if __name__ == "__main__":
#     action = sys.argv[1]
#     server_ip = '127.0.0.1'
#     server_port = 12345

#     if action == "create":
#         username = sys.argv[2]
#         create_room(server_ip, server_port, username)
#     elif action == "join":
#         token = sys.argv[2]
#         join_room(server_ip, server_port, token)
