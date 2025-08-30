from socket import *
import threading
from datetime import datetime

HOST = 'localhost'
PORT = 12345

server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"Server running on {HOST}:{PORT}...")

clients = {}  


def _timestamp():
    return datetime.now().strftime("%H:%M:%S")


def broadcast(message, exclude=None):
    stamped = f"[{_timestamp()}] {message}"
    dead = []
    for client in list(clients.keys()):
        if exclude is not None and client == exclude:
            continue
        try:
            client.send((stamped + "\n").encode())
        except:
            dead.append(client)
    for d in dead:
        try:
            d.close()
        except:
            pass
        clients.pop(d, None)
    print(f"{stamped}")

def _online_names(exclude=None):
    return [n for s, n in clients.items() if n and s != exclude]


def handle_client(client_socket):
    try:
        name = client_socket.recv(1024).decode().strip()
    except:
        clients.pop(client_socket, None)
        client_socket.close()
        return

    client_name = name if name else f"Guest{len(clients)}"
    clients[client_socket] = client_name

    online = _online_names(exclude=client_socket)
    banner_lines = [
        "Вітаємо в чаті!",
        "Команди: напишіть /quit щоб вийти.",
        f"Онлайн ({len(online)}): " + (", ".join(online) if online else "нікого немає"),
    ]
    for line in banner_lines:
        try:
            client_socket.send((f"[{_timestamp()}] {line}\n").encode())
        except:
            pass

    broadcast(f"{client_name} приєднався!", exclude=client_socket)

    announced_leave = False

    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                raise ConnectionError()
            message = data.decode().strip()
            if not message:
                continue
            if message.lower() in ("/quit", "exit"):
                broadcast(f"{client_name} вийшов!")
                announced_leave = True
                break
            broadcast(f"{client_name}: {message}")
            
        except:
            break

    left_name = clients.pop(client_socket, None)
    if not announced_leave and client_name:
        broadcast(f"{client_name} вийшов!")
    try:
        client_socket.close()
    except:
        pass


while True:
    client_socket, addr = server_socket.accept()
    
    clients.setdefault(client_socket, None)
        
    threading.Thread(target=handle_client, args=(client_socket,), daemon=True).start()
