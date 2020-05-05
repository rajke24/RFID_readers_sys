import json
import time
import paho.mqtt.client as mqtt
from datetime import datetime
from tinydb import where
from config import db, datetime_format, BROKER, TOPIC, PORT, CA_CRT_PATH, USERNAME, PASSWORD
from command import command_line

client = mqtt.Client()


def disconnect():
    time.sleep(4)
    client.loop_stop()


def connect_to_broker():
    client.tls_set(CA_CRT_PATH)
    client.username_pw_set(username=USERNAME, password=PASSWORD)
    client.connect(BROKER, PORT)
    client.on_message = on_message
    client.loop_start()
    client.subscribe(TOPIC)


def on_message(client, userdata, msg):
    data = json.loads(msg.payload)

    if not data['card_id'] or not data['terminal_id']:
        return

    time = datetime.now().strftime(datetime_format)
    found = db.table('terminals').search(where('id') == data['terminal_id'])
    if not found:
        print(f"Connection attempt from unknown terminal at time: {time}. TerminalID: {data['terminal_id']} ")
        return

    found_card = db.table('cards').search(where('id') == data['card_id'])
    if not found_card:
        db.table('unknown_logs').insert({'card_id': data['card_id'],
                                         'terminal_id': data['terminal_id'],
                                         'time': time})
        print(f"Login attempt by unknown card. CardID: {data['card_id']}")
    elif found_card[0]['assigned']:
        print(update_logs(data['card_id'], data['terminal_id']))
    else:
        print(f"Login attempt by unassigned card. CardID: {data['card_id']}")


def update_logs(card_id, terminal_id):
    logs = db.table('logs')
    person = db.table('people').search(where('card_id') == card_id)
    person_id = person[0]['id']
    found_log = logs.search((where('login_time') == '') |
                            (where('logout_time') == '') &
                            (where('card_id') == card_id))
    if not found_log:
        login_time = datetime.now().strftime(datetime_format)
        logs.insert({'person_id': person_id,
                     'card_id': card_id,
                     'terminal_id': terminal_id,
                     'login_time': str(login_time),
                     'logout_time': ''})
        return f"Person with ID {person_id} logged in"
    elif logs.search((where('login_time') != '') &
                     (where('logout_time') == '') &
                     (where('card_id') == card_id)):
        logout_time = datetime.now().strftime(datetime_format)
        logs.update({'logout_time': str(logout_time)}, (where('card_id') == card_id) & (where('logout_time') == ''))
        return f"Person with ID {person_id} logged out!"

    return "Unable to login or logout!"


def main():
    connect_to_broker()
    while not client.is_connected:
        time.sleep(1)

    command_line()
    disconnect()


if __name__ == "__main__":
    main()
