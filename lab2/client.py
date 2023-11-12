import socket
import configparser
from lab2.impl import solitaire_key_generator, stream_cipher, blum_blum_shub_key_generator


def client_main():
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

    # Connect to server
    host = 'localhost'
    port = 2000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

        # Send encrypted data
        message = b"Hello, encrypted Server!"
        encrypted_message = stream_cipher(message, key_generator, *key_args)
        s.sendall(encrypted_message)

        # Receive and decrypt the response from the server
        encrypted_response = s.recv(1024)
        if encrypted_response:
            response_message = stream_cipher(encrypted_response, key_generator, *key_args)
            print(f"Received from server: {response_message}")


# Run the client
client_main()
