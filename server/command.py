from csv import DictWriter
from tinydb import where
from config import db, fieldnames


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
        found = people.search(where('id') == person_id)
        if not found:
            people.insert({'id': person_id, 'name': data[3], 'card_id': ''})
            return "Person added successfully!"

        return "Person already exists! Aborted."

    if data[1] == "remove":
        if len(data) != 3:
            return "Incorrect argument number! Expected `person remove <person-id>`"

        person_id = data[2]
        found = people.search(where('id') == person_id)
        if found:
            person_card_id = found[0]['card_id']
            if person_card_id != '':
                db.table('cards').update({'assigned': False}, where('id') == person_card_id)
            people.remove(where('id') == person_id)

            return "Person removed successfully!"

        return "No such person exists!"

    if data[1] == "remove_card":
        if len(data) != 3:
            return "Incorrect argument number! Expected `person remove <person-id>`"

        person_id = data[2]
        found = people.search(where('id') == person_id)
        if found:
            person_card_id = found[0]['card_id']
            if person_card_id != '':
                db.table('cards').update({'assigned': False}, where('id') == person_card_id)
                people.update({'card_id': ''}, where('id') == person_id)
                return "Card removed from person successfully!"

        return "No such person exists!"

    if data[1] == "assign":
        if len(data) != 3:
            return "Incorrect argument number! Expected `person assign <person-id>`"

        person_id = data[2]
        found = people.search(where('id') == person_id)
        if found:
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


def log(data):
    logs = db.table('logs')

    if len(data) == 1:
        return "\n\t".join(("Available subcommands:", "list <person-id>", "gencsv <person-id>"))
    
    if data[1] == 'list':
        if len(data) != 3:
            return "Incorrect argument number! Expected `log list <person-id>`"

        person_id = data[2]

        found = db.table('people').search(where('id') == person_id)
        if not found:
            return "No such person exists!"

        found_log = logs.search(where('person_id') == person_id)
        if found_log:
            print(f"{'login_time':<19} \t logout_time")
            return "\n".join(f"{l['login_time']} \t {l['logout_time']}" for l in found_log)

    if data[1] == 'gencsv':
        if len(data) != 3:
            return "Incorrect argument number! Expected `log gencsv <person-id>`"

        person_id = data[2]
        found = db.table('people').search(where('id') == person_id)
        if found:
            found_log = logs.search(where('person_id') == person_id)
            if found_log:
                filename = '_'.join(('logs', person_id)) + '.csv'

                with open(filename, 'w', newline='') as csv_file:
                    csv_writer = DictWriter(csv_file, fieldnames=fieldnames, delimiter=',')
                    csv_writer.writeheader()
                    for log in found_log:
                        csv_row = {'terminal_id': log['terminal_id'],
                                  'login_time': str(log['login_time']),
                                  'logout_time': str(log['logout_time'])}
                        csv_writer.writerow(csv_row)
                return f"{filename} got created."

            return "Person has no logs yet."

        return "No such person exsists!"

    return "No such command"


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
