import socket
import threading
import configparser

from lab2.impl import solitaire_key_generator, stream_cipher, blum_blum_shub_key_generator


def handle_client(connection, address, key_generator, key_args):
    print(f"Connected to {address}")
    while True:
        # Receiving encrypted data from client
        encrypted_data = connection.recv(1024)
        if not encrypted_data:
            break

        # Decrypting the data
        decrypted_data = stream_cipher(encrypted_data, key_generator, *key_args)
        print(f"Received from {address}: {decrypted_data}")

        # Send a response back to client
        response_message = b"Message received"
        encrypted_response = stream_cipher(response_message, key_generator, *key_args)
        connection.sendall(encrypted_response)

    connection.close()
    print(f"Connection with {address} closed")


def server_main():
    # Load configuration
    config = configparser.ConfigParser()
    config.read('config.txt')
    algorithm_name = config['Encryption']['Algorithm']
    key_stream_length = int(config['Encryption']['KeyStreamLength'])

    # Select key generator
    if algorithm_name == 'Solitaire':
        key_generator = solitaire_key_generator
        some_fixed_seed = 123
        key_args = (key_stream_length, 52, some_fixed_seed)
    elif algorithm_name == 'Blum-Blum-Shub':
        key_generator = blum_blum_shub_key_generator
        key_args = (key_stream_length, 101, 103)
    else:
        raise ValueError("Unsupported algorithm")

    # Start server
    host = 'localhost'
    port = 2000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print("Server is listening...")

        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr, key_generator, key_args))
            client_thread.start()


server_main()
