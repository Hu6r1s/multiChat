import socket
import struct
import pickle
import threading

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('127.0.0.1', 123))
server_socket.listen()

clients_connected = {}
clients_data = {}
count = 1


def connection_requests():
    global count
    print('\033[38;5;11m', 'server start', '\033[0m')
    while True:
        client_socket, address = server_socket.accept()
        if len(clients_connected) == 100:
            client_socket.send('not_allowed'.encode('utf-8'))
            client_socket.close()
            continue
        else:
            client_socket.send('allowed'.encode('utf-8'))

        try:
            client_name = client_socket.recv(1024).decode('utf-8')
        except:
            print(f"{address} disconnected")
            client_socket.close()
            continue

        print('\033[38;5;10m', f"{client_name} 연결 {address} {len(clients_connected)}", '\033[0m')
        clients_connected[client_socket] = (client_name, count)

        image_size_bytes = client_socket.recv(1024)
        image_size_int = struct.unpack('i', image_size_bytes)[0]

        client_socket.send('received'.encode('utf-8'))
        image_extension = client_socket.recv(1024).decode('utf-8')

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

        if client_socket.recv(1024).decode('utf-8') == 'image_received':
            client_socket.send(struct.pack('i', count))

            for client in clients_connected:
                if client != client_socket:
                    client.send('notification'.encode('utf-8'))
                    data = pickle.dumps(
                        {'message': f"{clients_connected[client_socket][0]} 님이 입장했습니다", 'extension': image_extension,
                        'image_bytes': b, 'name': clients_connected[client_socket][0], 'n_type': 'joined', 'id': count})
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
            print(f"{clients_connected[client_socket][0]} disconnected")

            for client in clients_connected:
                if client != client_socket:
                    client.send('notification'.encode('utf-8'))

                    data = pickle.dumps({'message': f"{clients_connected[client_socket][0]} 님이 퇴장했습니다",'id': clients_connected[client_socket][1], 'n_type': 'left'})

                    data_length_bytes = struct.pack('i', len(data))
                    client.send(data_length_bytes)

                    client.send(data)

            del clients_data[clients_connected[client_socket][1]]
            del clients_connected[client_socket]
            client_socket.close()
            break
        except ConnectionAbortedError: #오류발생시
            print(f"{clients_connected[client_socket][0]} disconnected unexpectedly.")

            for client in clients_connected:
                if client != client_socket:
                    client.send('notification'.encode('utf-8'))
                    data = pickle.dumps({'message': f"{clients_connected[client_socket][0]} 님이 퇴장했습니다", 'id': clients_connected[client_socket][1], 'n_type': 'left'})
                    data_length_bytes = struct.pack('i', len(data))
                    client.send(data_length_bytes)
                    client.send(data)

            del clients_data[clients_connected[client_socket][1]]
            del clients_connected[client_socket]
            client_socket.close()
            break

        for client in clients_connected:
            if client != client_socket:
                client.send('message'.encode('utf-8'))
                client.send(data_bytes)


connection_requests()
