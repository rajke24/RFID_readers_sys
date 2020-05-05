from tinydb import TinyDB

BROKER = "laptop-Jarek"
TOPIC = "server/name"
CA_CRT_PATH = '../ca.crt'
PORT = 8883
USERNAME = 'server'
PASSWORD = 'server'

fieldnames = ['terminal_id', 'login_time', 'logout_time']
datetime_format = '%Y-%m-%d %H:%M:%S'

db = TinyDB("store.json", indent=4)
