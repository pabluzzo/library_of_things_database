import sqlite3
import tkinter as tk
from tkinter import ttk

con = sqlite3.connect("library.db", timeout = 5)
cur = con.cursor()

def main():

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
    return cur.fetchall()[0][0] # i have to specify [0][0] because for some reason it returns it as a tuple within a list

def get_person_data(id):
    name = get_datum("people", "name", id)
    contact = get_datum("people", "contact", id)
    note = get_datum("people", "note", id)
    currently_borrowing = cur.execute("SELECT item_id FROM location WHERE person_id = ?", (id,)).fetchall()
    owned_items = cur.execute("SELECT item_id FROM ownership WHERE person_id = ?", (id,)).fetchall()
    return id, name, contact, currently_borrowing, owned_items, note

def get_item_data(id):
    name = get_datum("items", "name", id)
    state = get_datum("items", "state", id)
    note = get_datum("items", "note", id)
    current_location = cur.execute("SELECT person_id FROM location WHERE item_id = ?", (id,)).fetchone()[0]
    owner = cur.execute("SELECT person_id FROM ownership WHERE item_id = ?", (id,)).fetchone()[0]
    return id, name, state, current_location, owner, note

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


def items_menu():
        itemsmenu = tk.Toplevel()
        itemsmenu.title("Items menu")
        itemsmenu.geometry("700x400")
        itemsmenu.grid_columnconfigure(0, weight=1)
        itemsmenu.grid_rowconfigure(0, weight=1)

        itemsframe = ttk.Frame(itemsmenu, padding="10")
        itemsframe.grid(column=0, row=0, sticky="nwes")
        for i in range(5):
            itemsframe.grid_columnconfigure(i, weight=1)

        itemsframe.grid_columnconfigure(0, weight=0, minsize=200)
        itemsframe.grid_columnconfigure(1, weight=0, minsize=100)
        itemsframe.grid_columnconfigure(2, weight=0, minsize=50)
        itemsframe.grid_columnconfigure(3, weight=0, minsize=50)
        itemsframe.grid_columnconfigure(4, weight=0, minsize=150)
        itemsframe.grid_columnconfigure(5, weight=0, minsize=100)

        # row 0 widgets
        ttk.Label(itemsframe, text="Items database", font=("Helvetica", 15)).grid(row=0, column=0)
        ttk.Button(itemsframe, text="+ New item").grid(row=0, column=1)
        ttk.Label(itemsframe, text="Name:").grid(row=0, column=3, sticky="sw")
        ttk.Button(itemsframe, text="edit").grid(row=0, column=4, sticky="sw")
        tk.Button(itemsframe, text="Delete\nitem", fg="red", anchor="center").grid(row=0, column=5, sticky="s")

        # search box & functions for placeholder "Search..." text
        search = tk.StringVar()
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
        # NOTE make name widget not wrap around but change font size?
        ttk.Button(itemsframe, text="Filters").grid(row=1, column=1)
        item_name_widget = tk.Label(itemsframe, font=("Helvetica", 25), wraplength=300)
        item_name_widget.grid(row=1, column=3, columnspan=3)

        items_list = tk.Listbox(itemsframe)
        items_list.grid(row=2, column=0, columnspan=2, rowspan=5, sticky="nwes")

        item_state_widget = ttk.Label(itemsframe, anchor="w")
        item_state_widget.grid(row=2, column=3, columnspan=2, sticky="w")
        ttk.Button(itemsframe, text="edit").grid(row=2, column=5)

        item_location_widget = ttk.Label(itemsframe, anchor="w")
        item_location_widget.grid(row=3, column=3, columnspan=2, sticky="w")
        ttk.Button(itemsframe, text="edit").grid(row=3, column=5)

        item_owner_widget = ttk.Label(itemsframe, anchor="w")
        item_owner_widget.grid(row=4, column=3, columnspan=2, sticky="w")
        ttk.Button(itemsframe, text="edit").grid(row=4, column=5)

        item_note_widget = ttk.Label(itemsframe, anchor="w", justify="left", wraplength=200)
        item_note_widget.grid(row=5, column=3, columnspan=2, sticky="w")
        ttk.Button(itemsframe, text="edit").grid(row=5, column=5)

        # ui polishing
        itemsframe.grid_columnconfigure(0, weight=1)
        for i in range(6):
            itemsframe.grid_rowconfigure(i, weight=1)
        for child in itemsframe.winfo_children():
            child.grid_configure(padx=5, pady=5)
        ttk.Separator(itemsframe, orient="vertical").grid(row=0, column=2, rowspan=7, sticky="ns")


        """
        ITEMS MENU FUNCTIONS
        """

        def load_itemsa():
            """
            Refreshes the contents of the item listbox
            """
            items_list.delete(0, tk.END)
            cur.execute("SELECT * FROM items ORDER BY name")
            items = cur.fetchall()
            for row in items:
                # inserts item name and ID in the listbox. ID is included because I could not think of
                # a better way to later retrieve it when the user selects the item from the listbox, as
                # the name by itself is not sufficient because it might not be unique in the database.
                items_list.insert(tk.END, [row[1], f"(ID:{row[0]})"])

        def load_item_data(event=None):
            """
            Updates UI labels when a new item is selected
            """
            try:
                selection = event.widget.curselection()
            except:
                pass


            if 'selection' in locals():
                # get all item data through the item's ID
                item_data = get_item_data(event.widget.get(selection[0])[1].strip("(ID: )"))

                # update widgets based on each item datum
                item_name_widget.configure(text=item_data[1])
                item_state_widget.configure(text=f"State: {item_data[2]}")
                item_location_widget.configure(text=f"Location: {get_person_data(item_data[3])[1]} (ID: {item_data[3]})")
                item_owner_widget.configure(text=f"Owner: {get_person_data(item_data[4])[1]} (ID: {item_data[4]})")
                item_note_widget.configure(text=f"Note: {item_data[5]}")
            else:
                item_name_widget.configure(text="No item selected")
                item_state_widget.configure(text="State: n/a")
                item_location_widget.configure(text="Location: n/a")
                item_owner_widget.configure(text="Owner: n/a")
                item_note_widget.configure(text="Note: n/a")

        items_list.bind("<<ListboxSelect>>", load_item_data)

        def load_items(event=None):
            # get current query from search box (if there is one)
            if search.get() == 'Search...':
                search_query = ''
            else:
                search_query = search.get()

            # filter Listbox items based on search query
            items_list.delete(0, tk.END)
            cur.execute("SELECT * FROM items WHERE name LIKE ? ORDER BY name", ('%' + search_query + '%',))
            items = cur.fetchall()
            for row in items:
                # inserts each item name and ID in the listbox. ID is included because I could not think of
                # a better way to later retrieve it when the user selects the item from the listbox, as
                # the name by itself is not sufficient because it might not be unique in the database.
                items_list.insert(tk.END, [row[1], f"(ID:{row[0]})"])
        search_box.bind("<KeyRelease>", load_items)

        load_items()
        load_item_data()
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
