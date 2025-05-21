import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

def main():
    con = sqlite3.connect("library.db", timeout = 5)
    cur = con.cursor()

    main_menu()

    con.close()

"""
General functions
"""
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

def commandline_menu():
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

"""
Application functions
"""
def items_menu():
        itemsmenu = tk.Toplevel()
        itemsmenu.title("Items menu")
        itemsmenu.geometry("700x400")
        itemsmenu.grid_columnconfigure(0, weight=1)
        itemsmenu.grid_rowconfigure(0, weight=1)

        #menu_item_id = tk.StringVar()
        #menu_item_id.set("Item ID:\nn/a")
        menu_item_name = tk.StringVar()
        menu_item_name.set("No item selected")
        menu_item_state = tk.StringVar()
        menu_item_state.set("State: n/a")
        menu_item_location = tk.StringVar()
        menu_item_location.set("Location: n/a")
        menu_item_owner = tk.StringVar()
        menu_item_owner.set("Owner: n/a")
        menu_item_note = tk.StringVar()
        menu_item_note.set("Note: n/a")
        search = tk.StringVar()

        itemsframe = ttk.Frame(itemsmenu, padding="10")
        itemsframe.grid(column=0, row=0, sticky="nwes")
        itemsframe.grid_columnconfigure(1, weight=1)
        for i in range(5):
            itemsframe.grid_columnconfigure(i, weight=1)

        # row 0 widgets
        ttk.Label(itemsframe, text="Items database", font=("Helvetica", 15)).grid(row=0, column=0)
        ttk.Button(itemsframe, text="+ New item").grid(row=0, column=1)
        ttk.Label(itemsframe, text="Name:").grid(row=0, column=3, sticky="sw")
        ttk.Button(itemsframe, text="edit").grid(row=0, column=4, sticky="sw")
        #ttk.Label(itemsframe, textvariable=menu_item_id, anchor="center").grid(row=0, column=5)
        tk.Button(itemsframe, text="Delete\nitem", fg="red", anchor="center").grid(row=0, column=5, sticky="s")

        # search box & functions for placeholder "Search..." text
        def on_entry_click(event):
            if search_box.get() == "Search...":
                search_box.delete(0, tk.END)
                search_box.config(foreground="black")
        def on_focus_out(event):
            if search_box.get() == "":
                search_box.insert(0, "Search...")
                search_box.config(foreground="grey")
        search_box = ttk.Entry(itemsframe, textvariable=search)
        search_box.grid(row=1, column=0, sticky="we")
        search_box.insert(0, 'Search...')
        search_box.config(foreground="grey")
        search_box.bind("<FocusIn>", on_entry_click)
        search_box.bind("<FocusOut>", on_focus_out)

        # other row 1 widgets
        ttk.Button(itemsframe, text="Filters").grid(row=1, column=1)
        tk.Label(itemsframe, textvariable=menu_item_name, font=("Helvetica", 30), wraplength=400).grid(row=1, column=3, columnspan=3)

        # Database listbox
        tk.Listbox(itemsframe).grid(row=2, column=0, columnspan=2, rowspan=5, sticky="nwes")

        # Item state
        ttk.Label(itemsframe, textvariable=menu_item_state, anchor="w").grid(row=2, column=3, columnspan=2, sticky="w")
        ttk.Button(itemsframe, text="edit").grid(row=2, column=5)

        # Item location
        ttk.Label(itemsframe, textvariable=menu_item_location, anchor="w").grid(row=3, column=3, columnspan=2, sticky="w")
        ttk.Button(itemsframe, text="edit").grid(row=3, column=5)

        # Item owner
        ttk.Label(itemsframe, textvariable=menu_item_owner, anchor="w").grid(row=4, column=3, columnspan=2, sticky="w")
        ttk.Button(itemsframe, text="edit").grid(row=4, column=5)

        #Item note
        ttk.Label(itemsframe, textvariable=menu_item_note, anchor="w", justify="left", wraplength=300).grid(row=5, column=3, columnspan=2, sticky="w")
        ttk.Button(itemsframe, text="edit").grid(row=5, column=5)

        # ui polishing
        itemsframe.grid_columnconfigure(0, weight=1)
        for i in range(6):
            itemsframe.grid_rowconfigure(i, weight=1)
        for child in itemsframe.winfo_children():
            child.grid_configure(padx=5, pady=5)
        ttk.Separator(itemsframe, orient="vertical").grid(row=0, column=2, rowspan=7, sticky="ns")

        itemsmenu.mainloop()

def main_menu():
    root = tk.Tk()
    root.title("Main menu")
    root.geometry("400x300")

    rootframe = ttk.Frame(root, padding="10")
    rootframe.grid(column=0, row=0, sticky="nwes")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    ttk.Label(rootframe, text="Library of things", anchor="center", font=("Helvetica", 30)).grid(row=0)
    ttk.Button(rootframe, text="Items", command=items_menu).grid(row=1)
    ttk.Button(rootframe, text="People").grid(row=2)
    ttk.Button(rootframe, text="Event log").grid(row=3)

    rootframe.grid_columnconfigure(0, weight=1)
    for i in range(4):
        rootframe.grid_rowconfigure(i, weight=1)
    for child in rootframe.winfo_children():
        child.grid_configure(padx=5, pady=5, sticky="nsew")

    root.mainloop()


if __name__ == '__main__':
    main()
