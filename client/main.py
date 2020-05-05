# import lib.rfid.MFRC522 as MFRC522

import paho.mqtt.client as mqtt
import os
import time
import json
from config import TOPIC, BROKER, CA_CRT_PATH, PORT, USERNAME, PASSWORD


def read_terminal_id():
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'terminals_id.txt')
        s = open(file_path, 'r', encoding="utf-8")
        terminal_id = s.read(12)
        s.close()
        print('Using terminal_id -', terminal_id)
        return terminal_id
    except Exception as exc:
        print("File open error:", exc)
        print('Using default terminal_id - "00000000"')
        return "00000000"


def main():
    terminal_id = read_terminal_id()
    client = mqtt.Client()

    client.tls_set(CA_CRT_PATH)
    client.username_pw_set(username=USERNAME, password=PASSWORD)
    client.connect(BROKER, PORT)

    while not client.is_connected:
        time.sleep(1)

    while True:
        data = input()
        if len(data) == 0:
            continue

        if data == 'exit':
            break

        client.publish(TOPIC, json.dumps({'card_id': data, 'terminal_id': terminal_id}))

    # client.disconnect()

    # MIFAREReader = MFRC522.MFRC522()
    # while True:
    #     (status, _) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
    #     if status == MIFAREReader.MI_OK:
    #         (status, uid) = MIFAREReader.MFRC522_Anticoll()
    #         if status == MIFAREReader.MI_OK:
    #             card_id = ''.join(uid)
    #             client.publish(topic, json.dumps({ 'card_id': card_id, 'terminal_id': terminal_id}))


if __name__ == "__main__":
    main()
