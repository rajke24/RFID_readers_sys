from tinydb import TinyDB

broker = "localhost"
topic = "andrzejewski/RFID_sys"

fieldnames = ['terminal_id', 'login_time', 'logout_time']
datetime_format = '%Y-%m-%d %H:%M:%S'

db = TinyDB("store.json", indent=4)
