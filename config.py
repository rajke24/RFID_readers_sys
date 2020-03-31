from tinydb import TinyDB

fieldnames = ['person_id', 'person_name', 'card_id', 'terminal_id', 'login_time', 'logout_time']
datetime_format = '%Y-%m-%d %H:%M:%S'

db = TinyDB("store.json", indent=4)
