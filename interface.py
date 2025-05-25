import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime

con = sqlite3.connect("library.db", timeout = 5)
cur = con.cursor()

def main():

    main_menu()
    con.close()

"""
General functions
"""
def add_person(name=None, contact=None, note=None):
    cur.execute("INSERT into people (name, contact, note) VALUES(?, ?, ?)", (name, contact, note))
    con.commit()

def add_item(name=None, state=None, note=None):
    cur.execute("INSERT into items (name, state, note) VALUES(?, ?, ?)", (name, state, note))
    con.commit()
    item_id = cur.lastrowid
    edit_ownership(item_id, 1) # sets default ownership to LIBRARY (ID: 1)
    edit_location(item_id, 1) # sets default location to LIBRARY (ID: 1)

def remove(table, id):
    """
    Things are not actually deleted because otherwise their ID would get assigned to
    the next new item. Instead, their data is anonymized and they are hidden from the UI.
    """
    if table == "people":
        log_event('delete', 'PERSON', id, get_person_data(id)[1])
        cur.execute("UPDATE people SET name = 'DELETED PERSON', contact = 'n/a', note = 'n/a' WHERE id = ?", (id,))
    elif table == "items":
        log_event('delete', 'ITEM', id, get_item_data(id)[1])
        cur.execute("UPDATE items SET name = 'DELETED ITEM', state = 'n/a', note = 'n/a' WHERE id = ?", (id,))
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
    try:
        cur.execute(f"SELECT {column} FROM {table} WHERE id = ?", (id,))
        return cur.fetchall()[0][0] # i have to specify [0][0] because for some reason it returns it as a tuple within a list
    except:
        return "n/a"

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

def edit_data(table, id, column, new_content):
    cur.execute(f"UPDATE {table} SET {column} = ? WHERE id = ?", (new_content, id))
    con.commit()

def log_event(event_type, object_type, object_id=None, name=None, field=None, old_value=None, new_value=None):
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # get current date and time for log
    if event_type == 'add':
        event = f'A new {object_type} has been added.'
    elif event_type == 'delete':
        event = f'{object_type} "{name}" (ID: {object_id}) has been deleted.'
    elif event_type == 'edit':
        event = f'The {field} of {object_type} "{name}" (ID: {object_id}) has been changed from "{old_value}" to "{new_value}"'
    cur.execute(f"INSERT INTO logs (time, event) VALUES(?, ?)", (time, event)) # log event

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
    ttk.Button(rootframe, text="People", command=people_menu).grid(row=2)
    ttk.Button(rootframe, text="Event logs", command=event_logs).grid(row=3)

    rootframe.grid_columnconfigure(0, weight=1)
    for i in range(4):
        rootframe.grid_rowconfigure(i, weight=1)
    for child in rootframe.winfo_children():
        child.grid_configure(padx=5, pady=5, sticky="nsew")

    root.mainloop()

def items_menu():

    def load_items(event=None):
        """
        Filters listbox based on user input in the searchbar.
        """
        # get current query from search box (if there is one)
        if search.get() == 'Search...':
            search_query = ''
        else:
            search_query = search.get()

        # filter Listbox items based on search query
        items_list.delete(0, tk.END)
        cur.execute("SELECT * FROM items WHERE name LIKE ? AND name NOT LIKE '%DELETED%' ORDER BY name", ('%' + search_query + '%',))
        items = cur.fetchall()
        for row in items:
            # inserts each item name and ID in the listbox. ID is included because I could not think of
            # a better way to later retrieve it when the user selects the item from the listbox, as
            # the name by itself is not sufficient because it might not be unique in the database.
            text = f"{row[1]} | (ID: {row[0]})"
            items_list.insert(tk.END, text)

    global last_item_selection
    last_item_selection = None
    def load_item_data(event=None):
        """
        Refreshes label widgets when a new item is selected
        """
        global last_item_selection

        try:
            selection = items_list.curselection()[0] # get index of currently selected item
            last_item_selection = selection # log last item selection as global variable
        except: # if nothing is selected:
            if last_item_selection == None: # if nothing has been selected yet, ideally only when menu is first opened
                item_name_value = "No item selected"
                item_state_value = "n/a"
                item_location_value = "n/a"
                item_owner_value = "n/a"
                item_note_value = "n/a"
            else: # if something had been selected in the past, fall back on last selection
                selection = last_item_selection

        if last_item_selection != None: # to not trigger this when menu first opens
            item_data = get_item_data(items_list.get(selection).split(" | ")[1].strip("(ID: )")) # get its data

            # assign data to widget textvariables
            item_name_value = item_data[1]
            item_state_value = item_data[2]
            item_location_value = f"{get_person_data(item_data[3])[1]} (ID: {item_data[3]})"
            item_owner_value = f"{get_person_data(item_data[4])[1]} (ID: {item_data[4]})"
            item_note_value = item_data[5]

        # update widgets
        item_name_widget.configure(text=f"{item_name_value}")
        item_state_widget.configure(text=f"State: {item_state_value}")
        item_location_widget.configure(text=f"Location: {item_location_value}")
        item_owner_widget.configure(text=f"Owner: {item_owner_value}")
        item_note_widget.configure(text=f"Note: {item_note_value}")

    def items_add_button(event=None):
        """
        Adds a new dummy item to the database, and automatically selects it for the user
        to edit its fields. By default, the item's owner and location is the library.
        If a dummy item already exists, it get selected without creating yet another one.
        """

        # check if a NEW ITEM already exists (to avoid user creating multiple empty items)
        new_items = cur.execute("SELECT COUNT(name) FROM items WHERE name = 'NEW ITEM'").fetchone()[0]
        if new_items == 0:
            add_item('NEW ITEM', 'n/a', 'n/a')
            log_event('add', 'ITEM')
            load_items()

        # find new item in listbox and select it
        index = None
        for i in range(items_list.size()):
            if items_list.get(i).startswith('NEW ITEM'):
                index = i
                break
        items_list.select_clear(0, tk.END) # unselect current item
        items_list.select_set(index) # select NEW ITEM
        items_list.activate(index) # highlight it
        items_list.see(index) # scroll to it
        items_list.event_generate("<<ListboxSelect>>") # refresh widgets. I did not use load_item_data() because
                                                        # for some reason it would not work. If I instead replicate
                                                        # the event of the user clicking on the listbox, it does. (??)

    def items_edit_button(column):
        """
        Called when user clicks "edit" next to a field.
        Opens a popup window for the user to enter the new value, while displaying the current value on top.
        """
        global last_item_selection
        selection = last_item_selection
        if selection != None:
            id = items_list.get(selection).split(" | ")[1].strip("(ID: )") # get item ID from database

            if get_item_data(id)[1].startswith('DELETED'): # don't show edit window if item is deleted
                return

            popup = tk.Toplevel()
            popup.title("Edit value")
            popup.geometry("400x400")

            # get current value to display to user
            current_value = tk.StringVar()
            current_value.set(cur.execute(f"SELECT {column} FROM items WHERE id = ?", (id,)).fetchone()[0])

            # ui widgets
            tk.Label(popup, text="Current value", font=('Helvetica', 15)).pack(pady=10)
            tk.Label(popup, textvariable=current_value).pack(pady=10)
            tk.Label(popup, text="Enter the new value:", font=('Helvetica', 15)).pack(pady=10)
            entry = tk.Text(popup, height=3, width=40, font=('Helvetica', 12))
            entry.insert("1.0", current_value.get())
            entry.pack(pady=10)
            tk.Label(popup, text="Note: changes will only be visible after clicking 'Refresh'\nnext to the searchbar. If you are editing something's name,\nsomething else might get selected when you refresh\nbecause the alphabetical order has changed. Sorry :/").pack(pady=10)

            def edit_value(id, column):
                """
                Called when user clicks "Confirm" in the popup window.
                Edits the value in the database and closes the popup window.
                """
                new_value = entry.get("1.0", tk.END).strip() # get new value from user input
                if new_value:
                    # get data for event log
                    name = cur.execute(f"SELECT name FROM items WHERE id = ?", (id,)).fetchone()[0]
                    old_value = cur.execute(f"SELECT {column} FROM items WHERE id = ?", (id,)).fetchone()[0]
                    log_event('edit', 'ITEM', id, name, column, old_value, new_value) # log event

                    cur.execute(f"UPDATE items SET {column} = ? WHERE id = ?", (new_value, id)) # update database
                    con.commit()
                    popup.destroy()
                else:
                    pass # in case input field is still empty

            tk.Button(popup, text="Confirm", command=lambda: edit_value(id, column)).pack(pady=10)
            tk.Button(popup, text="Cancel", command=popup.destroy).pack(pady=5)
        else:
            pass

    def items_remove_button():
        """
        Deletes currently selected item with a confirmation popup.
        """
        # check if item is selected
        global last_item_selection
        selection = last_item_selection
        if selection != None:
            id = items_list.get(selection).split(" | ")[1].strip("(ID: )") # get item ID from database

            if get_item_data(id)[1].startswith('DELETED'):
                messagebox.showwarning("Warning", 'Item already deleted. To make it disappear from the list, click on "Refresh" next to the searchbar.')
            else:
                popup = tk.Toplevel()
                popup.title("Confirm deletion")
                popup.geometry("300x200")

                # ui widgets
                tk.Label(popup, text="Are you sure you want\nto delete this item?", font=('Helvetica', 15)).pack(pady=10)

                def delete(id):
                    remove('items', id)
                    popup.destroy()

                tk.Button(popup, text="Confirm", command=lambda: delete(id)).pack(pady=10)
                tk.Button(popup, text="Cancel", command=popup.destroy).pack(pady=5)
        else:
            pass

    def items_edit_person_button(): #TODO
        """
        Called when user clicks on "edit" for either location or ownership field.
        """

    itemsmenu = tk.Toplevel()
    itemsmenu.title("Items menu")
    itemsmenu.geometry("700x400")
    itemsmenu.grid_columnconfigure(0, weight=1)
    itemsmenu.grid_rowconfigure(0, weight=1)

    itemsframe = ttk.Frame(itemsmenu, padding="10")
    itemsframe.grid(column=0, row=0, sticky="nwes")
    for i in range(5):
        itemsframe.grid_columnconfigure(i, weight=1)

    # adjust grid size
    itemsframe.grid_columnconfigure(0, weight=0, minsize=200)
    itemsframe.grid_columnconfigure(1, weight=0, minsize=100)
    itemsframe.grid_columnconfigure(2, weight=0, minsize=50)
    itemsframe.grid_columnconfigure(3, weight=0, minsize=50)
    itemsframe.grid_columnconfigure(4, weight=0, minsize=150)
    itemsframe.grid_columnconfigure(5, weight=0, minsize=100)

    # row 0 widgets
    ttk.Label(itemsframe, text="Items database", font=("Helvetica", 15)).grid(row=0, column=0)
    ttk.Button(itemsframe, text="+ New item", command=items_add_button).grid(row=0, column=1)
    tk.Button(itemsframe, text="Delete\nitem", fg="red", anchor="center", command=items_remove_button).grid(row=0, column=5, sticky="s")

    # search box & functions for placeholder "Search..." text
    search = tk.StringVar()
    def search_focus_in(event):
        if search_box.get() == "Search...":
            search_box.delete(0, tk.END)
            search_box.config(foreground="black")
    def search_focus_out(event):
        if search_box.get() == "":
            search_box.insert(0, "Search...")
            search_box.config(foreground="grey")
    search_box = ttk.Entry(itemsframe, textvariable=search)
    search_box.grid(row=1, column=0, sticky="we")
    search_box.insert(0, 'Search...')
    search_box.config(foreground="grey")
    search_box.bind("<FocusIn>", search_focus_in)
    search_box.bind("<FocusOut>", search_focus_out)
    # bind load_items function to searchbox when user types
    search_box.bind("<KeyRelease>", load_items)

    # listbox
    items_list = tk.Listbox(itemsframe)
    items_list.grid(row=2, column=0, columnspan=2, rowspan=5, sticky="nwes")
    # bind widget refresh to user selecting something in the listbox
    items_list.bind("<<ListboxSelect>>", load_item_data)

    def manual_refresh():
        global last_item_selection
        try:
            selection = last_item_selection
            try:
                items_list.select_set(selection)
            except:
                items_list.select_set(selection - 1) # in case the selected item was last of the listbox after deleting an item
        except:
            pass
        load_items()
        load_item_data()
    ttk.Button(itemsframe, text="Refresh", command=manual_refresh).grid(row=1, column=1)

    ttk.Label(itemsframe, text="Name:").grid(row=0, column=3, sticky="sw")
    item_name_value = None
    item_name_widget = tk.Label(itemsframe, font=("Helvetica", 25), height=2, wraplength=300)
    item_name_widget.grid(row=1, column=3, columnspan=3)
    ttk.Button(itemsframe, text="edit", command=lambda: items_edit_button("name")).grid(row=0, column=4, sticky="sw")

    item_state_value = None
    item_state_widget = ttk.Label(itemsframe, anchor="w")
    item_state_widget.grid(row=2, column=3, columnspan=2, sticky="w")
    ttk.Button(itemsframe, text="edit", command=lambda: items_edit_button("state")).grid(row=2, column=5)

    item_location_value = None
    item_location_widget = ttk.Label(itemsframe, anchor="w")
    item_location_widget.grid(row=3, column=3, columnspan=2, sticky="w")
    ttk.Button(itemsframe, text="edit").grid(row=3, column=5)

    item_owner_value = None
    item_owner_widget = ttk.Label(itemsframe, anchor="w")
    item_owner_widget.grid(row=4, column=3, columnspan=2, sticky="w")
    ttk.Button(itemsframe, text="edit").grid(row=4, column=5)

    item_note_value = None
    item_note_widget = ttk.Label(itemsframe, anchor="w", justify="left", wraplength=200)
    item_note_widget.grid(row=5, column=3, columnspan=2, sticky="w")
    ttk.Button(itemsframe, text="edit", command=lambda: items_edit_button("note")).grid(row=5, column=5)

    # ui polishing
    itemsframe.grid_columnconfigure(0, weight=1)
    for i in range(6):
        itemsframe.grid_rowconfigure(i, weight=1)
    for child in itemsframe.winfo_children():
        child.grid_configure(padx=5, pady=5)
    ttk.Separator(itemsframe, orient="vertical").grid(row=0, column=2, rowspan=7, sticky="ns")

    load_items()
    load_item_data()
    itemsmenu.mainloop()

def people_menu():
    """
    WARNING TO SCIENTIFIC PROGRAMMING STAFF: people_menu is basically a copy of items_menu but with fewer features.
    Don't waste your time checking it, it's literally identical.
    I know it's veeery sloppy, but I realised too late it would have been better to just have every menu in one single
    window, with maybe a button to switch between items. I could only make few 'universal' functions because the rest
    would need to refer to things within the window.
    I've already worked so long on this... so I just mostly copy-and-pasted. Sorry...
    """

    def load_people(event=None):
        """
        Filters listbox based on user input in the searchbar.
        """
        # get current query from search box (if there is one)
        if search.get() == 'Search...':
            search_query = ''
        else:
            search_query = search.get()

        # filter Listbox people based on search query
        people_list.delete(0, tk.END)
        cur.execute("SELECT * FROM people WHERE name LIKE ? AND name NOT LIKE '%DELETED%' ORDER BY name", ('%' + search_query + '%',))
        people = cur.fetchall()
        for row in people:
            # inserts each person name and ID in the listbox. ID is included because I could not think of
            # a better way to later retrieve it when the user selects the person from the listbox, as
            # the name by itself is not sufficient because it might not be unique in the database.
            text = f"{row[1]} | (ID: {row[0]})"
            people_list.insert(tk.END, text)

    global last_person_selection
    last_person_selection = None
    def load_person_data(event=None):
        """
        Refreshes label widgets when a new person is selected
        """
        global last_person_selection

        try:
            selection = people_list.curselection()[0] # get index of currently selected person
            last_person_selection = selection # log last person selection as global variable
        except: # if nothing is selected:
            if last_person_selection == None: # if nothing has been selected yet, ideally only when menu is first opened
                person_name_value = "No person selected"
                person_contact_value = "n/a"
                person_borrowing_value = "n/a"
                person_owns_value = "n/a"
                person_note_value = "n/a"
            else: # if something had been selected in the past, fall back on last selection
                selection = last_person_selection

        if last_person_selection != None: # to not trigger this when menu first opens
            person_data = get_person_data(people_list.get(selection).split(" | ")[1].strip("(ID: )")) # get its data

            # assign data to widget textvariables
            person_name_value = person_data[1]
            person_contact_value = person_data[2]
            person_borrowing_value = f"Nothing yet"
            person_owns_value = f"Nothing yet"
            person_note_value = person_data[5]

        # update widgets
        person_name_widget.configure(text=f"{person_name_value}")
        person_contact_widget.configure(text=f"contact: {person_contact_value}")
        person_borrowing_widget.configure(text=f"borrowing: {person_borrowing_value}")
        person_owns_widget.configure(text=f"owns: {person_owns_value}")
        person_note_widget.configure(text=f"Note: {person_note_value}")

    def people_add_button(event=None):
        """
        Adds a new dummy person to the database, and automatically selects it for the user
        to edit its fields.
        If a dummy person already exists, it get selected without creating yet another one.
        """

        # check if a NEW person already exists (to avoid user creating multiple empty people)
        new_people = cur.execute("SELECT COUNT(name) FROM people WHERE name = 'NEW PERSON'").fetchone()[0]
        if new_people == 0:
            add_person('NEW PERSON', 'n/a', 'n/a')
            log_event('add', 'PERSON')
            load_people()

        # find new person in listbox and select it
        index = None
        for i in range(people_list.size()):
            if people_list.get(i).startswith('NEW PERSON'):
                index = i
                break
        people_list.select_clear(0, tk.END) # unselect current person
        people_list.select_set(index) # select NEW person
        people_list.activate(index) # highlight it
        people_list.see(index) # scroll to it
        people_list.event_generate("<<ListboxSelect>>") # refresh widgets. I did not use load_person_data() because
                                                        # for some reason it would not work. If I instead replicate
                                                        # the event of the user clicking on the listbox, it does. (??)

    def people_edit_button(column):
        """
        Called when user clicks "edit" next to a field.
        Opens a popup window for the user to enter the new value, while displaying the current value on top.
        """
        global last_person_selection
        selection = last_person_selection
        if selection != None:
            id = people_list.get(selection).split(" | ")[1].strip("(ID: )") # get person ID from database

            if get_person_data(id)[1].startswith('DELETED'): # don't show edit window if person is deleted
                return

            popup = tk.Toplevel()
            popup.title("Edit value")
            popup.geometry("400x400")

            # get current value to display to user
            current_value = tk.StringVar()
            current_value.set(cur.execute(f"SELECT {column} FROM people WHERE id = ?", (id,)).fetchone()[0])

            # ui widgets
            tk.Label(popup, text="Current value", font=('Helvetica', 15)).pack(pady=10)
            tk.Label(popup, textvariable=current_value).pack(pady=10)
            tk.Label(popup, text="Enter the new value:", font=('Helvetica', 15)).pack(pady=10)
            entry = tk.Text(popup, height=3, width=40, font=('Helvetica', 12))
            entry.insert("1.0", current_value.get())
            entry.pack(pady=10)
            tk.Label(popup, text="Note: changes will only be visible after clicking 'Refresh'\nnext to the searchbar. If you are editing something's name,\nsomething else might get selected when you refresh\nbecause the alphabetical order has changed. Sorry :/").pack(pady=10)

            def edit_value(id, column):
                """
                Called when user clicks "Confirm" in the popup window.
                Edits the value in the database and closes the popup window.
                """
                new_value = entry.get("1.0", tk.END).strip() # get new value from user input
                if new_value:
                    # get data for event log
                    name = cur.execute(f"SELECT name FROM people WHERE id = ?", (id,)).fetchone()[0]
                    old_value = cur.execute(f"SELECT {column} FROM people WHERE id = ?", (id,)).fetchone()[0]
                    log_event('edit', 'PERSON', id, name, column, old_value, new_value) # log event

                    cur.execute(f"UPDATE people SET {column} = ? WHERE id = ?", (new_value, id)) # update database
                    con.commit()
                    popup.destroy()
                else:
                    pass # in case input field is still empty

            tk.Button(popup, text="Confirm", command=lambda: edit_value(id, column)).pack(pady=10)
            tk.Button(popup, text="Cancel", command=popup.destroy).pack(pady=5)
        else:
            pass

    def people_remove_button():
        """
        Deletes currently selected person with a confirmation popup.
        """
        # check if person is selected
        global last_person_selection
        selection = last_person_selection
        if selection != None:
            id = people_list.get(selection).split(" | ")[1].strip("(ID: )") # get person ID from database
            if id == '1':
                messagebox.showwarning("Warning", 'Cannot delete library')
            elif get_person_data(id)[1].startswith('DELETED'):
                messagebox.showwarning("Warning", 'Person already deleted. To make it disappear from the list, click on "Refresh" next to the searchbar.')
            else:
                popup = tk.Toplevel()
                popup.title("Confirm deletion")
                popup.geometry("300x200")

                # ui widgets
                tk.Label(popup, text="Are you sure you want\nto delete this person?", font=('Helvetica', 15)).pack(pady=10)

                def delete(id):
                    remove('people', id)
                    popup.destroy()

                tk.Button(popup, text="Confirm", command=lambda: delete(id)).pack(pady=10)
                tk.Button(popup, text="Cancel", command=popup.destroy).pack(pady=5)
        else:
            pass

    peoplemenu = tk.Toplevel()
    peoplemenu.title("People menu")
    peoplemenu.geometry("700x400")
    peoplemenu.grid_columnconfigure(0, weight=1)
    peoplemenu.grid_rowconfigure(0, weight=1)

    peopleframe = ttk.Frame(peoplemenu, padding="10")
    peopleframe.grid(column=0, row=0, sticky="nwes")
    for i in range(5):
        peopleframe.grid_columnconfigure(i, weight=1)

    # adjust grid size
    peopleframe.grid_columnconfigure(0, weight=0, minsize=200)
    peopleframe.grid_columnconfigure(1, weight=0, minsize=100)
    peopleframe.grid_columnconfigure(2, weight=0, minsize=50)
    peopleframe.grid_columnconfigure(3, weight=0, minsize=50)
    peopleframe.grid_columnconfigure(4, weight=0, minsize=150)
    peopleframe.grid_columnconfigure(5, weight=0, minsize=100)

    # row 0 widgets
    ttk.Label(peopleframe, text="People database", font=("Helvetica", 15)).grid(row=0, column=0)
    ttk.Button(peopleframe, text="+ New person", command=people_add_button).grid(row=0, column=1)
    tk.Button(peopleframe, text="Delete\nperson", fg="red", anchor="center", command=people_remove_button).grid(row=0, column=5, sticky="s")

    # search box & functions for placeholder "Search..." text
    search = tk.StringVar()
    def search_focus_in(event):
        if search_box.get() == "Search...":
            search_box.delete(0, tk.END)
            search_box.config(foreground="black")
    def search_focus_out(event):
        if search_box.get() == "":
            search_box.insert(0, "Search...")
            search_box.config(foreground="grey")
    search_box = ttk.Entry(peopleframe, textvariable=search)
    search_box.grid(row=1, column=0, sticky="we")
    search_box.insert(0, 'Search...')
    search_box.config(foreground="grey")
    search_box.bind("<FocusIn>", search_focus_in)
    search_box.bind("<FocusOut>", search_focus_out)
    # bind load_people function to searchbox when user types
    search_box.bind("<KeyRelease>", load_people)

    # listbox
    people_list = tk.Listbox(peopleframe)
    people_list.grid(row=2, column=0, columnspan=2, rowspan=5, sticky="nwes")
    # bind widget refresh to user selecting something in the listbox
    people_list.bind("<<ListboxSelect>>", load_person_data)

    def manual_refresh():
        global last_person_selection
        try:
            selection = last_person_selection
            try:
                people_list.select_set(selection)
            except:
                people_list.select_set(selection - 1) # in case the selected person was last of the listbox after deleting an person
        except:
            pass
        load_people()
        load_person_data()
    ttk.Button(peopleframe, text="Refresh", command=manual_refresh).grid(row=1, column=1)

    ttk.Label(peopleframe, text="Name:").grid(row=0, column=3, sticky="sw")
    person_name_value = None
    person_name_widget = tk.Label(peopleframe, font=("Helvetica", 25), height=2, wraplength=300)
    person_name_widget.grid(row=1, column=3, columnspan=3)
    ttk.Button(peopleframe, text="edit", command=lambda: people_edit_button("name")).grid(row=0, column=4, sticky="sw")

    person_contact_value = None
    person_contact_widget = ttk.Label(peopleframe, anchor="w")
    person_contact_widget.grid(row=2, column=3, columnspan=2, sticky="w")
    ttk.Button(peopleframe, text="edit", command=lambda: people_edit_button("contact")).grid(row=2, column=5)

    person_borrowing_value = None
    person_borrowing_widget = ttk.Label(peopleframe, anchor="w")
    person_borrowing_widget.grid(row=3, column=3, columnspan=3, sticky="w")

    person_owns_value = None
    person_owns_widget = ttk.Label(peopleframe, anchor="w")
    person_owns_widget.grid(row=4, column=3, columnspan=3, sticky="w")

    person_note_value = None
    person_note_widget = ttk.Label(peopleframe, anchor="w", justify="left", wraplength=200)
    person_note_widget.grid(row=5, column=3, columnspan=2, sticky="w")
    ttk.Button(peopleframe, text="edit", command=lambda: people_edit_button("note")).grid(row=5, column=5)

    # ui polishing
    peopleframe.grid_columnconfigure(0, weight=1)
    for i in range(6):
        peopleframe.grid_rowconfigure(i, weight=1)
    for child in peopleframe.winfo_children():
        child.grid_configure(padx=5, pady=5)
    ttk.Separator(peopleframe, orient="vertical").grid(row=0, column=2, rowspan=7, sticky="ns")

    load_people()
    load_person_data()
    peoplemenu.mainloop()

def event_logs():
    logsmenu = tk.Toplevel()
    logsmenu.title("Event logs")
    logsmenu.geometry("700x700")
    logsmenu.grid_columnconfigure(0, weight=1)
    logsmenu.grid_rowconfigure(0, weight=1)

    logsframe = ttk.Frame(logsmenu, padding="10")
    logsframe.grid(column=0, row=0, sticky="nwes")

    # allow widgets to expand
    logsframe.grid_columnconfigure(0, weight=1)
    logsframe.grid_rowconfigure(1, weight=1)

    def load_logs(event=None):
        # get current query from search box (if there is one)
        if search_event.get() == 'Search event...':
            search_event_query = ''
        else:
            search_event_query = search_event.get()

        # filter Listbox items based on search query
        logs_list.delete(0, tk.END)
        cur.execute("SELECT * FROM logs WHERE event LIKE ? ORDER BY time DESC", ('%' + search_event_query + '%',))
        logs = cur.fetchall()
        for row in logs:
            # insert each log in the listbox (date, event).
            text = f"{row[1]} | {row[2]}"
            logs_list.insert(tk.END, text)

    # search box setup
    search_event = tk.StringVar()

    def search_event_focus_in(event):
        if search_event_box.get() == "Search event...":
            search_event_box.delete(0, tk.END)
            search_event_box.config(foreground="black")

    def search_event_focus_out(event):
        if search_event_box.get() == "":
            search_event_box.insert(0, "Search event...")
            search_event_box.config(foreground="grey")

    search_event_box = ttk.Entry(logsframe, textvariable=search_event)
    search_event_box.insert(0, 'Search event...')
    search_event_box.config(foreground="grey")
    search_event_box.bind("<FocusIn>", search_event_focus_in)
    search_event_box.bind("<FocusOut>", search_event_focus_out)
    search_event_box.bind("<KeyRelease>", load_logs) # bind load_logs function to searchbox when user types
    search_event_box.grid(row=0, column=0, sticky="ew", padx=5, pady=5) # resize searchbar

    # listbox
    logs_list = tk.Listbox(logsframe)
    # bind widget refresh to user selecting something in the listbox
    logs_list.bind("<<ListboxSelect>>", load_logs)
    # resize Listbox
    logs_list.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    load_logs()
    logsmenu.mainloop()


if __name__ == '__main__':
    main()
