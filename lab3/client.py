import json
import sys
from random import randint
from socket import socket, AF_INET, SOCK_STREAM

sys.path.append('../lab4')
from generators.solitaire import Solitaire
from util.cipher import Cipher
from util.crypto.merkle_hellman import generate_private_key, create_public_key, encrypt_mh, decrypt_mh
from key_server import HOST_NAME, KEY_SERVER_PORT, MESSAGE_SIZE

offset = 0


def initialize_connection(port) -> socket:
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind((HOST_NAME, port))
    print('Client listening on port {} for connection'.format(port))
    sock.listen(1)

    while True:
        connection, _ = sock.accept()
        try:
            # print('Sending initial message')
            connection.sendall(json.dumps({
                'status': 'init',
            }).encode())
            data = json.loads(connection.recv(MESSAGE_SIZE).decode())
            # print('Received data: {}'.format(data))
            if 'status' in data and data['status'] == 'connected':
                return connection
        except Exception:
            print('Exception while connecting. Waiting for another connection')


def connect(port) -> socket:
    sock = socket(AF_INET, SOCK_STREAM)
    # print('Client connecting to port {}'.format(PORT))
    sock.connect((HOST_NAME, port))

    try:
        data = json.loads(sock.recv(MESSAGE_SIZE).decode())
        # print('Received data: {}'.format(data))
        if 'status' in data and data['status'] == 'init':
            sock.sendall(json.dumps({'status': 'connected'}).encode())
            return sock
        print('Could not connect')
        exit()
    except Exception:
        print('Could not connect')
        exit()


def initialize_cipher(nr_it):
    seed = [*range(1, 55)]
    generator = Solitaire(seed)
    generator.skip(nr_it)
    return Cipher(Solitaire(generator.seed))


def register_pub_key(connection: socket, id: int, key: bytes) -> bool:
    connection.sendall(
        json.dumps({
            'method': 'POST',
            'id': id,
            'key': key
        }).encode()
    )
    ans = json.loads(connection.recv(MESSAGE_SIZE).decode())
    return ans['success']


def get_pub_key(connection: socket, id: int) -> bytes:
    connection.sendall(
        json.dumps({
            'method': 'GET',
            'id': id
        }).encode()
    )
    ans = json.loads(connection.recv(MESSAGE_SIZE).decode())
    return ans['key']


def disconnect_from_key_server(connection: socket, id: int):
    connection.sendall(
        json.dumps({
            'method': 'CLOSE',
            'id': id
        }).encode()
    )
    connection.close()


def send_mh_encr(connection: socket, message, public_key):
    connection.sendall(json.dumps(encrypt_mh(message.encode(), public_key)).encode())


def recv_mh_encr(connection: socket, private_key):
    return decrypt_mh(json.loads(connection.recv(MESSAGE_SIZE).decode()), private_key).decode()


def send_sol_encr(connection: socket, cipher: Cipher) -> int:
    plain_text = input('Enter your message:\n')
    if plain_text == '':
        print('Leaving')
        connection.sendall(json.dumps({'status': 'exit'}).encode())
        connection.close()
        exit()
    connection.sendall(
        json.dumps({
            'offset': cipher.get_offset(),
            'cipher_text': list(cipher.encrypt(bytes(plain_text, 'ascii')))
        }).encode()
    )
    return len(plain_text)


def recv_sol_encr(connection: socket, cipher: Cipher) -> str:
    data = json.loads(connection.recv(MESSAGE_SIZE).decode())
    if 'status' in data and data['status'] == 'exit':
        print('Peer left the connection')
        connection.close()
        exit()
    if 'offset' not in data or 'cipher_text' not in data:
        return 'Invalid message received.'
    msg_offset = data['offset']
    cipher_text = data['cipher_text']
    return cipher.decrypt(bytes(cipher_text), msg_offset).decode()


def main():
    if len(sys.argv) <= 2:
        print('Missing argument.')
        print('Usage: {} {{id}} {{1|2}}'.format(sys.argv[0]))
        exit()
    id_str = sys.argv[1]
    id = int(id_str)
    if sys.argv[2] in ['1', 'first']:
        first_sender = True
    elif sys.argv[2] in ['2', 'second']:
        first_sender = False
    else:
        print('Incorrect argument.')
        print('Usage: {} {{id}} {{1|2}}'.format(sys.argv[0]))
        exit()

    # register to key server with generated public key
    private_key = generate_private_key()
    public_key = create_public_key(private_key)
    print('private and public keys generated')
    key_server_socket = connect(KEY_SERVER_PORT)
    print('connected to key server')
    while not register_pub_key(key_server_socket, id, public_key):
        pass
    print('public key sent to key server')

    if first_sender:
        # read the id of peer
        peer_id = int(input('id of peer = '))
        peer_socket = connect(peer_id)

        # get the public key of peer from key server
        peer_public_key = get_pub_key(key_server_socket, peer_id)
        disconnect_from_key_server(key_server_socket, id)
        print('public key of peer received from key server')

        # say hello to peer
        send_mh_encr(peer_socket, id_str, peer_public_key)
        if peer_id != int(recv_mh_encr(peer_socket, private_key)):
            print("Error: received id does not matches with known id.")
        print('connected to peer with id {}'.format(peer_id))
    else:
        # get the id of peer from hello message
        peer_socket = initialize_connection(id)
        peer_id = int(recv_mh_encr(peer_socket, private_key))
        print('peer with id {} connected'.format(peer_id))

        # get the public key of peer from key server
        peer_public_key = get_pub_key(key_server_socket, peer_id)
        disconnect_from_key_server(key_server_socket, id)
        print('public key of peer received from key server')

        # respond to hello message
        send_mh_encr(peer_socket, id_str, peer_public_key)

    # make seed for solitaire
    nr_it_1 = randint(0, 64)
    print('half solitaire key generated')
    send_mh_encr(peer_socket, str(nr_it_1), peer_public_key)
    nr_it_2 = int(recv_mh_encr(peer_socket, private_key))
    print('half solitaire key received')
    cipher = initialize_cipher(nr_it_1 + nr_it_2)
    print('cipher initalized')

    # start communication
    if first_sender:
        send_sol_encr(peer_socket, cipher)

    while True:
        msg = recv_sol_encr(peer_socket, cipher)
        print('Peer messaged you:')
        print(msg)
        send_sol_encr(peer_socket, cipher)


if __name__ == '__main__':
    main()
