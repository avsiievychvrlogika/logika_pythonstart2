from socket import *
import threading

client_socket = socket(AF_INET, SOCK_STREAM)
name = input("Введіть ваше ім'я (нік): ")

HOST, PORT = 'localhost', 12345
client_socket.connect((HOST, PORT))
client_socket.send(name.encode())

def send_message():
    while True:
        message = input("Повідомлення (або /quit): ")
        
        client_socket.send(message.encode())
        if message.lower() in ("/quit", "exit"):
            client_socket.close()
            break

threading.Thread(target=send_message, daemon=True).start()

while True:
    try:
        response = client_socket.recv(1024).decode().strip()
        if response:
            print(f"{response}")
    except:
        break

client_socket.close()
