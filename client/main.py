import paho.mqtt.client as mqtt
import os
import time
import json
from config import TOPIC, BROKER, CA_CRT_PATH, PORT, USERNAME, PASSWORD


def read_terminal_id():
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'terminals_id.txt')
        with open(file_path) as f:
            terminal_id = f.read(12)
        print('Using terminal_id -', terminal_id)
        return terminal_id
    except Exception as exc:
        print("File open error:", exc)
        print('Using default terminal_id - "00000000"')
        return "00000000"


def main():
    terminal_id = read_terminal_id()
    # creating mqtt.Client instance
    client = mqtt.Client()
    # configure network encryption, enable TLS/SSL support
    client.tls_set(CA_CRT_PATH)
    # set a username and a password for broker authentication
    client.username_pw_set(username=USERNAME, password=PASSWORD)
    # connect client to a broker and to the network port of the server host
    client.connect(BROKER, PORT)

    while not client.is_connected:
        time.sleep(1)

    # insert card ID and publish its id and terminal id to a server until inserted data != 'exit'
    while True:
        data = input("Insert your card: ")
        if len(data) == 0:
            continue

        if data == 'exit':
            break

        client.publish(TOPIC, json.dumps({'card_id': data, 'terminal_id': terminal_id}))


if __name__ == "__main__":
    main()
