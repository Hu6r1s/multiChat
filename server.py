<<<<<<< HEAD
import socket
import threading

names = {}
rooms = {}
clients = {}

def broadcast(soc, msg, option):
    soc.sendall('ROOM_INSERT'.encode('utf-8'))
    room_soc = soc.recv(1024).decode('utf-8')
    for group in rooms[room_soc]:
        if option == 1:
            n = names[group]
            soc.sendall(n.encode('utf-8'))
            msg = ''
        group.sendall(msg.encode('utf-8'))

def handle(soc, addr):
    while True:
        data = soc.recv(1024)
        msg = data.decode('utf-8')
        if msg == '/quit':
            msg = names[soc] + ' 님이 퇴장했습니다.'
            broadcast(soc, msg, 0)
            soc.sendall(data)
            break
        elif msg == '/user':
            broadcast(soc, msg, 1)
        elif msg == '/room':
            room_list = list(rooms.keys())
            for value in room_list:
                soc.sendall(value.encode('utf-8'))
        else:
            msg = names[soc] + ' : ' + msg
            broadcast(soc, msg, 0)
    soc.close()
    print('\033[38;5;9m',names[soc], addr, '해제', '\033[0m')
    remove(addr)
    del clients[addr]
    del names[soc]

def remove(addr):
    for value in list(rooms.values()):
        if len(rooms) == 1 and len(value) == 1:
            rooms.clear()
        elif clients[addr] in value and 2 <= len(value):
            a = value.index(clients[addr])
            del value[a]
        elif clients[addr] in value and 1 == len(value):
            for key in list(rooms):
                if rooms[key] == [clients[addr]]:
                    del rooms[key]

def information(client, addr):
    client.sendall('NICKNAME_INSERT'.encode('utf-8'))
    name = client.recv(1024).decode('utf-8')
    names[client] = name

    clients[addr] = client

    client.sendall('ROOM_INSERT'.encode('utf-8'))
    room = client.recv(1024).decode('utf-8')
    if room in rooms:
        rooms[room].extend([client])
    else:
        rooms[room] = [client]

if __name__ == "__main__":
    HOST = '172.17.147.80'
    PORT = 12321

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print('\033[38;5;11m', 'server start', '\033[0m')

    while True:
        soc, addr = server_socket.accept()
        information(soc, addr)
        print('\033[38;5;10m',names[soc], addr, '연결', '\033[0m')
        msg = names[soc] + ' 님이 입장했습니다.'
        broadcast(soc, msg, 0)
        t = threading.Thread(target=handle, args=(soc, addr))
        t.start()

