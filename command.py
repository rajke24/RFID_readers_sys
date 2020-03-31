from csv import DictWriter
from datetime import datetime
from tinydb import where
from config import db, datetime_format, fieldnames
from random import randrange
from os import path


def terminal(input_data):
    terminals = db.table('terminals')

    if len(input_data) == 1:
        return "\n\t".join(('Available subcommands:',
                            'list', 'add <terminal-id>', 'remove <terminal-id>'))

    if input_data[1] == 'list':
        print("ID")
        list = "\n".join(t['id'] for t in terminals)
        return list

    if input_data[1] == 'add':
        if len(input_data) != 3:
            return 'Passed command is incorrect ! Expected `terminal add <terminal-id>` '

        terminal_id = input_data[2]
        found = terminals.search(where('id') == terminal_id)

        if not found:
            terminals.insert({'id': terminal_id})
            return "Terminal added successfully !"
        else:
            return "Terminal already added !"

    if input_data[1] == 'remove':
        if len(input_data) != 3:
            return 'Passed command is incorrect! Expected `terminal remove <terminal-id>` '

        terminal_id = input_data[2]
        found = terminals.search(where('id') == terminal_id)

        if found:
            terminals.remove(where('id') == terminal_id)
            return "Terminal removed successfully !"
        else:
            return "Terminal not found !"

    return "No such command"


def cards(input_data):
    cards = db.table('cards')
    if len(input_data) == 1:
        return "\n\t".join(('Available subcommands:', 'list'))

    if input_data[1] == 'list':
        print("{:<17}".format("CardID") + "Assigned")
        return "\n".join(f"{c['id']} \t {c['assigned']}" for c in cards)

    return "No such command"


def person(data):
    people = db.table('people')
    if len(data) == 1:
        return "\n\t".join(
            ("Available subcommands:",
             "list", "add <person-id> <name>", "remove <person-id>", "remove_card <person-id>", "assign <person-id>"))

    if data[1] == "list":
        print("{:<8}".format("ID") + "\t" + "{:<15}".format("Name") + "\t" + "CardID")
        return '\n'.join("{:<8}".format(p['id']) + "\t" + "{:<15}".format(p['name']) + "\t" + p['card_id'] for p in people)

    if data[1] == "add":
        if len(data) != 4:
            return "Incorrect argument number! Expected `person add <person-id> <name>`"

        person_id = data[2]
        search = people.search(where('id') == person_id)
        if not search:
            people.insert({'id': person_id, 'name': data[3], 'card_id': ''})
            return "Person added successfully!"

        return "Person already exists! Aborted."

    if data[1] == "remove":
        if len(data) != 3:
            return "Incorrect argument number! Expected `person remove <person-id>`"

        person_id = data[2]
        search = people.search(where('id') == person_id)
        if search:
            person_card_id = search[0]['card_id']
            if person_card_id != '':
                db.table('cards').update({'assigned': False}, where('id') == person_card_id)
            people.remove(where('id') == person_id)

            return "Person removed successfully!"

        return "No such person exists!"

    if data[1] == "remove_card":
        if len(data) != 3:
            return "Incorrect argument number! Expected `person remove <person-id>`"

        person_id = data[2]
        search = people.search(where('id') == person_id)
        if search:
            person_card_id = search[0]['card_id']
            if person_card_id != '':
                db.table('cards').update({'assigned': False}, where('id') == person_card_id)
                people.update({'card_id': ''}, where('id') == person_id)
                return "Card removed from person successfully!"

        return "No such person exists!"

    if data[1] == "assign":
        if len(data) != 3:
            return "Incorrect argument number! Expected `person assign <person-id>`"

        person_id = data[2]
        search = people.search(where('id') == person_id)
        if search:
            card_search = db.table('cards').search(where('assigned') == False)
            if card_search[0]:
                card_id = card_search[0]['id']
                people.update({'card_id': card_id}, where('id') == person_id)
                db.table('cards').update({'assigned': True}, where('id') == card_id)
                return "Person got the card assigned successfully!"
            elif len(card_search) == 0:
                return "There are no more cards to assign"

            return "No such card exists!"

        return "No such person exists!"

    return "No such command!"


def log(input_data):
    logs = db.table('logs')

    if len(input_data) == 1:
        return "\n\t".join(("Available subcommands:", "list", "read <person-id>"))
    
    if input_data[1] == 'list':
        return "\n".join(f"{l['login_time']} \t {l['logout_time']}" for l in logs)

    if input_data[1] == 'read':
        if len(input_data) != 3:
            return "Incorrect argument number! Expected `log read <card-id>`"

        if len((db.table('terminals'))) == 0:
            return "Sorry, no terminals to read card"
        else:
            random = randrange(len(db.table('terminals'))) - 1
            terminal_id = db.table('terminals').search(where('id'))[random]['id']

        person_id = input_data[2]
        person_search = db.table('people').search(where('id') == person_id)
        if not person_search:
            return "No such person exists"

        card_id = person_search[0]['card_id']
        person_name = person_search[0]['name']

        if card_id == '':
            return "No card assigned to person"

        search_card = db.table('cards').search(where('id') == card_id)
        if not search_card:
            unknown_logs = db.table('unknown_logs')
            currentDT = datetime.now().strftime(datetime_format)
            unknown_logs.insert({'terminal_id': terminal_id,
                                 'card_id': card_id,
                                 'log_time': currentDT})
            return "Unknown card"

        search = logs.search((where('login_time') == '') | (where('logout_time') == ''))
        if not search:
            login_time = datetime.now().strftime(datetime_format)
            logs.insert({'person_id': person_id,
                         'person_name': person_name,
                         'card_id': card_id,
                         'terminal_id': terminal_id,
                         'login_time': str(login_time),
                         'logout_time': ''})
            return f"Person with ID {person_id} logged in"
        else:
            logout_time = datetime.now().strftime(datetime_format)
            logs.update({'logout_time': str(logout_time)}, where('person_id') == person_id)

            filename = '_'.join(('logs', person_id)) + '.csv'
            login_time = search[0]['login_time']
            csv_row = {'person_id': person_id, 'person_name': person_name,
                        'card_id': card_id, 'terminal_id': terminal_id,
                        'login_time': str(login_time), 'logout_time': str(logout_time)}

            if not path.exists(filename):
                with open(filename, 'w') as csv_file:
                    csv_writer = DictWriter(csv_file, fieldnames=fieldnames, delimiter=",")
                    csv_writer.writeheader()
                    csv_writer.writerow(csv_row)
            else:
                with open(filename, 'a+') as csv_file:
                    csv_writer = DictWriter(csv_file, fieldnames=fieldnames, delimiter=",")
                    csv_writer.writerow(csv_row)

        return f"Person with ID {person_id} logged out"


def command_line():
    print('\n> ', end='')
    input_data = input().split()

    if len(input_data) == 0:
        return command_line()

    if input_data[0] == 'terminal':
        print(terminal(input_data))
        return command_line()

    if input_data[0] == 'card':
        print(cards(input_data))
        return command_line()

    if input_data[0] == 'person':
        print(person(input_data))
        return command_line()

    if input_data[0] == 'log':
        print(log(input_data))
        return command_line()

    if input_data[0] == 'exit':
        print('Closing command line...')
        return

    print("Available commands:", "terminal", "card", "person", "log", "exit", sep="\n\t")
    return command_line()
