import socket
import struct
import threading
import json

class ChatServer:
  def __init__(self, host='127.0.0.1', port_tcp=12345, port_udp=12346): 
      self.host = host
      self.port_tcp = port_tcp
      self.port_udp = port_udp
      
      # TCPソケットの作成
      self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      
      # ソケットオプション設定
      self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      
      # UDPソケットの作成
      self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

      # バインド処理
      self.tcp_socket.bind((self.host, self.port_tcp))
      self.udp_socket.bind((self.host, self.port_udp))

      self.rooms = {}
      self.lock = threading.Lock()

  def start(self):
      self.tcp_socket.listen()
      print(f"Server listening on TCP {self.host}:{self.port_tcp} and UDP on {self.port_udp}")
      threading.Thread(target=self.handle_udp_messages).start()
      while True:
          client_socket, addr = self.tcp_socket.accept()
          threading.Thread(target=self.handle_client, args=(client_socket, addr)).start()

  def handle_client(self, client_socket, addr):
      while True:
          try:
              header = client_socket.recv(32)
              if not header:
                  break
              room_name_size, operation, state = struct.unpack('B B B', header[:3])
              operation_payload_size = int.from_bytes(header[3:], 'big')
              payload = client_socket.recv(operation_payload_size)

              # Handling different operations based on the command received from client
              if operation == 1 and state == 0:
                  username = payload.decode('utf-8')
                  token = self.create_room(username, addr)
                  response = {'status': 1, 'token': token}
                  print(f"Sending response to client: {response}")  # デバッグ出力
                  client_socket.sendall(json.dumps(response).encode())
              elif operation == 2 and state == 0:
                  token = payload.decode('utf-8')
                  self.join_room(client_socket, token, addr)

          except Exception as e:
              print(f"Error handling client {addr}: {e}")
              break
      client_socket.close()

  def handle_udp_messages(self):
      while True:
          data, addr = self.udp_socket.recvfrom(4096)
          try:
              room_name_size, token_size = struct.unpack('B B', data[:2])
              room_name = data[2:2 + room_name_size].decode('utf-8')
              token = data[2 + room_name_size:2 + room_name_size + token_size].decode('utf-8')
              message = data[2 + room_name_size + token_size:]
              with self.lock:
                  if token in self.rooms:
                      clients = self.rooms[token]['clients']
                      for client in clients:
                          if client != addr:
                              self.udp_socket.sendto(message, client)
          except Exception as e:
              print(f"Error processing UDP message from {addr}: {e}")

if __name__ == "__main__":
    server = ChatServer()
    server.start()


# import socket
# import struct
# import threading
# import json

# class ChatServer:
#     def __init__(self, host='127.0.0.1', port=12345):
#         self.host = host
#         self.port = port
#         self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.rooms = {}  # 各トークンに基づくチャットルームの情報を保持
#         self.lock = threading.Lock()

#     def start(self):
#         self.server_socket.bind((self.host, self.port))
#         self.server_socket.listen()
#         print(f"Server listening on {self.host}:{self.port}")
#         while True:
#             client_socket, addr = self.server_socket.accept()
#             threading.Thread(target=self.handle_client, args=(client_socket, addr)).start()

#     def handle_client(self, client_socket, addr):
#         while True:
#             try:
#                 header = client_socket.recv(32)
#                 if not header:
#                     break  # ヘッダーが空ならクライアントが切断されたと判断

#                 room_name_size, operation, state = struct.unpack('B B B', header[:3])
#                 operation_payload_size = int.from_bytes(header[3:], 'big')
#                 payload = client_socket.recv(operation_payload_size)

#                 if operation == 1 and state == 0:  # 新しいチャットルームの作成要求
#                     username = payload.decode('utf-8')
#                     token = self.create_room(username, addr)
#                     # 状態1: 準拠。トークンをクライアントに送り返す。
#                     response = {'status': 1, 'token': token}
#                     client_socket.sendall(json.dumps(response).encode())
#                     # 状態2: 完了。作成成功のメッセージを送る。
#                     completion_response = {'status': 2, 'message': 'Room created successfully'}
#                     client_socket.sendall(json.dumps(completion_response).encode())
#                 elif operation == 2 and state == 0:  # チャットルームへの参加要求
#                     token = payload.decode('utf-8')
#                     self.join_room(client_socket, token, addr)
                    
#             except Exception as e:
#                 print(f"Error handling client {addr}: {e}")
#                 break
#         client_socket.close()

#     def create_room(self, username, addr):
#         token = f"{addr[0]}:{addr[1]}:{username}"  # トークン生成
#         with self.lock:
#             self.rooms[token] = {"name": username, "host": addr, "clients": {addr}}
#         return token

#     def join_room(self, client_socket, token, addr):
#         with self.lock:
#             if token in self.rooms and addr in self.rooms[token]['clients']:
#                 self.rooms[token]['clients'].add(addr)
#                 client_socket.sendall(json.dumps({'status': 2, 'message': 'Joined the room'}).encode())
#             else:
#                 client_socket.sendall(json.dumps({'status': 0, 'message': 'Invalid token or IP address'}).encode())
#         client_socket.close()  # 参加処理後、TCP接続を終了

# if __name__ == "__main__":
#     server = ChatServer()
#     server.start()



# import socket
# import struct
# import threading
# import json

# class ChatServer:
#     def __init__(self, host='127.0.0.1', port=12345):
#         self.host = host
#         self.port = port
#         self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.rooms = {}
#         self.lock = threading.Lock()

#     def start(self):
#         self.server_socket.bind((self.host, self.port))
#         self.server_socket.listen()
#         print(f"Server listening on {self.host}:{self.port}")
#         while True:
#             client_socket, addr = self.server_socket.accept()
#             threading.Thread(target=self.handle_client, args=(client_socket, addr)).start()

#     def handle_client(self, client_socket, addr):
#         while True:
#             try:
#                 header = client_socket.recv(32)
#                 if not header:
#                     break

#                 room_name_size, operation, state = struct.unpack('B B B', header[:3])
#                 operation_payload_size = int.from_bytes(header[3:], 'big')
#                 payload = client_socket.recv(operation_payload_size)

#                 if operation == 1 and state == 0:  # Create new room request
#                     username = payload.decode('utf-8')
#                     token = self.create_room(username, addr)
#                     # Send response for compliance (status 1)
#                     response = {'status': 1, 'token': token}
#                     client_socket.sendall(json.dumps(response).encode())
#                     # Additional step to confirm completion (state 2)
#                     completion_response = {'status': 2, 'message': 'Room created successfully'}
#                     client_socket.sendall(json.dumps(completion_response).encode())
                    
#             except Exception as e:
#                 print(f"Error handling client {addr}: {e}")
#                 break
#         client_socket.close()

#     def create_room(self, username, addr):
#         token = f"{addr[0]}:{addr[1]}:{username}"
#         with self.lock:
#             self.rooms[token] = {"name": username, "host": addr, "clients": {addr}}
#         return token

# if __name__ == "__main__":
#     server = ChatServer()
#     server.start()
