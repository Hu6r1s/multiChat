# 클라이언트 코드
import socket, threading
import tkinter as tk
import os

# 전역변수
client_socket = None  # 서버와 1:1 통신할 소켓
label = None  # 레이블, 채팅내용
Msg = None  # 입력박스
root = None


def send(e):  # 이벤트 핸들러함수. 엔트리 엔터입력시 호출.
    global client_socket

    msg = Msg.get()  # 입력박스에 입력한 텍스트 읽어옴
    client_socket.sendall(msg.encode('utf-8'))
    Msg.delete(0, tk.END)


def th_read():
    global client_socket
    while True:
        data = client_socket.recv(1024)
        msg = data.decode('utf-8')
        # print(msg)


        if msg == 'NICKNAME_INSERT':
            client_socket.send(nickname.encode('utf-8'))
        elif msg == 'ROOM_INSERT':
            client_socket.send(room.encode('utf-8'))
        elif msg == '/quit':
            print('종료')
            client_socket.close()
            os._exit(1)
        else:
            label.configure(text=label.cget('text') + '\n' + msg)

    print('서버 메시지 출력 쓰레드 종료')


def ui_init():
    global label
    global Msg
    global root

    root = tk.Tk()  # 윈도우 창

    root.title('chatting room')  # 윈도우 제목창 타이틀 출력
    root.geometry("400x400")  # 윈도우 가로 세로 길이
    frm = tk.Frame(root)  # 윈도우에 프레임을 생성. 화면분할용도

    # 레이블 생성
    label = tk.Label(root, text='', relief='groove', borderwidth=1, padx=400, pady=150)
    # 입력박스 생성
    Msg = tk.Entry(root, width=100)
    Msg.bind('<Return>', send)
    # 버튼 생성
    # btn = tk.Button(root, text="send", command = send)

    # 위젯들을 프레임에 부착
    Msg.pack()
    frm.pack()
    label.pack()
    # btn.pack()
    
    


if __name__ == "__main__":
    #global root
    #global client_socket

    HOST = '121.185.122.63'
    PORT = 12321

    # 통신할 소켓 오픈
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 서버에 연결요청. server ip, port
    client_socket.connect((HOST, PORT))

    nickname = input("이름입력 : ")
    room = input("방입력 : ")

    ui_init()

    t2 = threading.Thread(target=th_read, args=())
    t2.start()

    root.mainloop()
    # client_socket.close()