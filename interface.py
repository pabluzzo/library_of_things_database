import sqlite3
from tkinter import *
from tkinter import ttk

con = sqlite3.connect("library.db", timeout = 5)
cur = con.cursor()

def main():
    menu()
    con.close()


def add_person(name='', contact='', note=''):
    cur.execute("INSERT into people (name, contact, note) VALUES(?, ?, ?)", (name, contact, note))
    con.commit()

def add_item(name="", state="", note=""):
    cur.execute("INSERT into items (name, state, note) VALUES(?, ?, ?)", (name, state, note))
    con.commit()

def remove(table, id):
    if table == "people":
        pass #todo bc what happens to all ownership / vouches / etc?
    cur.execute("DELETE FROM ? WHERE id = ?", (table, id))
    con.commit()

def edit_ownership(item_id, person_id):
    cur.execute("DELETE FROM ownership WHERE item_id = ?", (item_id,))
    cur.execute("INSERT INTO ownership (item_id, person_id) VALUES(?, ?)", (item_id, person_id))
    con.commit()

def edit_location(item_id, person_id):
    cur.execute("DELETE FROM location WHERE item_id = ?", (item_id,))
    cur.execute("INSERT INTO location (item_id, person_id) VALUES(?, ?)", (item_id, person_id))
    con.commit()

def get_datum(table, column, id):
    """
    Returns one datapoint in a table where an "id" field is present, i.e. people, items.
    """
    cur.execute(f"SELECT {column} FROM {table} WHERE id = ?", (id,))
    return cur.fetchall()

def get_person_data(id):
    name = get_datum("people", "name", id)
    contact = get_datum("people", "contact", id)
    note = get_datum("people", "note", id)
    currently_borrowing = cur.execute("SELECT item_id FROM location WHERE person_id = ?", (id,)).fetchone()
    owned_items = cur.execute("SELECT item_id FROM ownership WHERE person_id = ?", (id,)).fetchone()
    return id, name, contact, note, currently_borrowing, owned_items

def get_item_data(id):
    name = get_datum("items", "name", id)
    state = get_datum("items", "state", id)
    note = get_datum("items", "note", id)
    current_location = cur.execute("SELECT person_id FROM location WHERE item_id = ?", (id,)).fetchone()
    owner = cur.execute("SELECT person_id FROM ownership WHERE item_id = ?", (id,)).fetchone()
    return id, name, state, note, current_location, owner

def menu():
    """
    This is a command line placeholder menu to test whether my functions work.
    It is not meant to deal with invalid input.
    """

    on = 1
    menu = 0
    action = 0

    while on == 1:
        while menu == 0 and on == 1:
            action = int(input("""
What do you want to do?
1 = Item actions
2 = Person actions
3 = Location & ownership
0 = Exit
Your answer: """))
            if action == 0:
                on = 0
            else:
                menu = action

        while menu == 1:
            action = int(input("""
Item actions:
1 = View all items
2 = View item details
3 = Add an item
4 = Remove an item
5 = Edit an item
0 = Back to main menu
Your answer: """))
            if action == 0:
                menu = 0
            elif action == 1:
                for line in cur.execute("SELECT * from items"):
                    print(line)
            elif action == 2:
                print(get_item_data(int(input("Item ID: "))))
            elif action == 3:
                name = input("Item name: ")
                state = int(input("Item state (1=good, 2=damaged, 3=lost, 4=disposed): "))
                if state == 1:
                    state = 'good'
                elif state == 2:
                    state = 'damaged'
                elif state == 3:
                    state = 'lost'
                elif state == 4:
                    state == 'disposed'
                note = input("Item note: ")
                add_item(name, state, note)
            elif action == 4:
                print("Action not supported yet")
            elif action == 5:
                print("Action not supported yet")
            print("Action hopefully achieved!")
            menu = 0

        while menu == 2:
            action = int(input("""
Person actions:
1 = View all people
2 = Add a person
3 = Remove a person
4 = Edit a person
0 = Back to main menu
Your answer: """))
            if action == 0:
                menu = 0
            elif action == 1:
                for line in cur.execute('SELECT * FROM people'):
                    print(line)
            elif action == 2:
                name = input('Persons name: ')
                contact = input('Contact info: ')
                note = input('Note: ')
                add_person(name, contact, note)
            elif action == 3:
                print("Action not supported yet")
            elif action == 4:
                print("Action not supported yet")
            print("Action hopefully achieved!")
            menu = 0

        while menu == 3:
            action = int(input("""
Location & ownership:
1 = Edit an item's location ('possessor')
2 = Edit an item's ownership
0 = Back to main menu
Your answer: """))
            if action == 0:
                menu = 0
            elif action == 1:
                item_id = int(input("Item ID: "))
                person_id = int(input("New possessor's ID: "))
                edit_location(item_id, person_id)
            elif action == 2:
                item_id = int(input("Item ID: "))
                person_id = int(input("New owner's ID: "))
                edit_ownership(item_id, person_id)
            print("Action hopefully achieved!")
            menu = 0

if __name__ == '__main__':
    main()
