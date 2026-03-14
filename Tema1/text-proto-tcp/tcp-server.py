import socket
import threading

HOST = "127.0.0.1"
PORT = 3333
BUFFER_SIZE = 1024

class State:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()

    def add(self, key, value):
        with self.lock:
            if key in self.data:
                return "Key already exists"
            self.data[key] = value
        return f"{key} added"

    def get(self, key):
        with self.lock:
            return self.data.get(key, "Key not found")

    def remove(self, key):
        with self.lock:
            if key in self.data:
                del self.data[key]
                return f"{key} removed"
            return "Key not found"

    def list(self):
        with self.lock:
            lista_elemente = []
            if not self.data:
                return "List empty!"
            for key in self.data.keys():
                lista_elemente.append(f"{key}={self.data.get(key)}")
            return ",".join(lista_elemente)


    def count(self):
        with self.lock:
            count = len(self.data)
            return f"List has {count} elements!!!"

    def clear(self):
        with self.lock:
            self.data.clear()
            return "all data deleted :("

    def update(self, key, newValue):
        if key in self.data:
            self.data[key] = newValue
            return f"Data updated for key {key}"
        return "Key not found"

    def pop(self, key):
        if key in self.data:
            element = self.data[key]
            self.data.pop(key)
            return f"Value is {element}. This element has been deleted."
        return "Key not found"


state = State()

def process_command(command):
    parts = command.split()
    if len(parts) < 1:
        return "Invalid command format"

    cmd = parts[0]
    if cmd == "list" and len(parts) == 1:
        return state.list()
    elif cmd == "count" and len(parts) == 1:
        return state.count()
    elif cmd == "clear" and len(parts) == 1:
        return state.clear()
    elif cmd == "quit" and len(parts) == 1:
        return "BYEEEEE!"
    
    if len(parts) < 2:
        return "Invalid command format"
    
    cmd, key = parts[0], parts[1]
    if cmd == "add" and len(parts) > 2:
        return state.add(key, ' '.join(parts[2:]))
    elif cmd == "get" and len(parts) == 2:
        return state.get(key)
    elif cmd == "remove" and len(parts) == 2:
        return state.remove(key)
    elif cmd == "update" and len(parts) > 2:
        return state.update(key, ' '.join(parts[2:]))
    elif cmd == "pop" and len(parts) == 2:
        return state.pop(key)
    
    return "Invalid command"

def handle_client(client_socket):
    with client_socket:
        while True:
            try:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break

                command = data.decode('utf-8').strip()
                response = process_command(command)
                
                response_data = f"{len(response)} {response}".encode('utf-8')
                client_socket.sendall(response_data)

                if response == "BYEEEEE!":
                    print("[SERVER] Client wants to disconnect.")
                    break

            except Exception as e:
                client_socket.sendall(f"Error: {str(e)}".encode('utf-8'))
                break

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"[SERVER] Listening on {HOST}:{PORT}")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"[SERVER] Connection from {addr}")
            threading.Thread(target=handle_client, args=(client_socket,)).start()


if __name__ == "__main__":
    start_server()
