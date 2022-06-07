import socket
import struct
import pickle
import threading
import time
import random

HOST = '127.0.0.1'
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

clients_connected = {}
clients_data = {}
rooms = {}
count = 1


def connection_requests():
    global count
    print('\033[38;5;11m', 'server start', '\033[0m')
    while True:
        global client_socket, address
        client_socket, address = server_socket.accept()
        if len(clients_connected) == 100:
            client_socket.send('not_allowed'.encode())
            client_socket.close()
            continue
        else:
            client_socket.send('allowed'.encode())

        try:
            global client_name
            global room
            client_name = client_socket.recv(1024).decode()
            client_room = client_socket.recv(1024).decode()

        except:
            print('\033[38;5;9m', f"{client_name} 해제 {address} 접속자 {len(clients_connected)-1}명", '\033[0m')
            client_socket.close()
            continue

        print('\033[38;5;10m', f"{client_name} 연결 {address} 접속자 {len(clients_connected) + 1}명", '\033[0m')
        clients_connected[client_socket] = (client_name, count, client_room)

        image_size_bytes = client_socket.recv(1024)
        image_size_int = struct.unpack('i', image_size_bytes)[0]

        client_socket.send('received'.encode())
        image_extension = client_socket.recv(1024).decode()

        b = b''
        while True:
            image_bytes = client_socket.recv(1024)
            b += image_bytes
            if len(b) == image_size_int:
                break

        clients_data[count] = (client_name, b, image_extension)

        clients_data_bytes = pickle.dumps(clients_data)
        clients_data_length = struct.pack('i', len(clients_data_bytes))

        client_socket.send(clients_data_length)
        client_socket.send(clients_data_bytes)

        if client_socket.recv(1024).decode() == 'image_received':
            client_socket.send(struct.pack('i', count))

            for client in clients_connected:
                if client != client_socket and clients_connected[client][2] == clients_connected[client_socket][2]:
                    client.send('notification'.encode())
                    data = pickle.dumps({'message': f"{clients_connected[client_socket][0]} 님이 입장했습니다", 'extension': image_extension,'image_bytes': b, 'name': clients_connected[client_socket][0], 'n_type': 'joined', 'id': count, 'room': clients_connected[client_socket][2]})
                    num = random.uniform(0, 0.3)
                    time.sleep(num)
                    data_length_bytes = struct.pack('i', len(data))
                    client.send(data_length_bytes)
                    client.send(data)

        count += 1
        t = threading.Thread(target=receive_data, args=(client_socket,))
        t.start()


def receive_data(client_socket):
    while True:
        try:
            data_bytes = client_socket.recv(1024)
        except ConnectionResetError:
            print('\033[38;5;9m', f"{client_name} 해제 {address} 접속자 {len(clients_connected) - 1}명", '\033[0m')
            for client in clients_connected:
                if client != client_socket and clients_connected[client][2] == clients_connected[client_socket][2]:
                    client.send('notification'.encode())

                    data = pickle.dumps({'message': f"{clients_connected[client_socket][0]} 님이 퇴장했습니다",'id': clients_connected[client_socket][1], 'n_type': 'left'})

                    num = random.uniform(0, 0.3)
                    time.sleep(num)
                    data_length_bytes = struct.pack('i', len(data))
                    client.send(data_length_bytes)

                    client.send(data)

            del clients_data[clients_connected[client_socket][1]]
            del clients_connected[client_socket]
            client_socket.close()
            break
        except ConnectionAbortedError:
            print('\033[38;5;9m', f"{client_name} 해제 {address} 접속자 {len(clients_connected) - 1}명", '\033[0m')
            for client in clients_connected:
                if client != client_socket and clients_connected[client][2] == clients_connected[client_socket][2]:
                    client.send('notification'.encode())
                    data = pickle.dumps({'message': f"{clients_connected[client_socket][0]} 님이 퇴장했습니다", 'id': clients_connected[client_socket][1], 'n_type': 'left'})
                    num = random.uniform(0, 0.3)
                    time.sleep(num)
                    data_length_bytes = struct.pack('i', len(data))
                    client.send(data_length_bytes)
                    client.send(data)

            del clients_data[clients_connected[client_socket][1]]
            del clients_connected[client_socket]
            client_socket.close()
            break

        for client in clients_connected:
            if client != client_socket and clients_connected[client][2] == clients_connected[client_socket][2]:
                client.send('message'.encode())
                client.send(data_bytes)


connection_requests()