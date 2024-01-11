import json
import threading
from socket import socket, AF_INET, SOCK_STREAM

HOST_NAME = 'localhost'
KEY_SERVER_PORT = 4242
MESSAGE_SIZE = 1024

PUBLIC_KEYS = {}


def serve_client(client_socket: socket):
    while True:
        try:
            data = json.loads(client_socket.recv(MESSAGE_SIZE).decode())
            if 'method' not in data.keys() or 'id' not in data.keys():
                client_socket.sendall(json.dumps({'success': False}).encode())
            elif data['method'] == 'CLOSE':
                client_socket.close()
                return
            elif data['method'] == 'GET':
                print('Key {} was requested.'.format(PUBLIC_KEYS[data['id']]))
                client_socket.sendall(
                    json.dumps({
                        'success': True,
                        'key': PUBLIC_KEYS[data['id']]
                    }).encode()
                )
            elif data['method'] == 'POST':
                PUBLIC_KEYS[data['id']] = data['key']
                print('Client {} registered with key {}'.format(data['id'], data['key']))
                client_socket.sendall(json.dumps({'success': True}).encode())
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
        # Handle JSON decode error

        except Exception as e:
            print(f"General exception: {e}")


def initialize_connection() -> socket:
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind((HOST_NAME, KEY_SERVER_PORT))
    print('Server listening on port {} for connection'.format(KEY_SERVER_PORT))
    sock.listen(2)

    while True:
        connection, _ = sock.accept()
        try:
            print('Sending initial message')
            connection.sendall(json.dumps({
                'status': 'init',
            }).encode())
            data = json.loads(connection.recv(MESSAGE_SIZE).decode())
            print('Received data: {}'.format(data))
            if 'status' in data and data['status'] == 'connected':
                serve_client_thread = threading.Thread(target=serve_client, args=(connection,))
                serve_client_thread.start()
        except Exception as e:
            print(e)
            print('Exception while connecting. Waiting for another connection')


if __name__ == '__main__':
    initialize_connection()
