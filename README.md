# library_of_things_database
**Requires the following python libraries**: datetime, sqlite3, tkinter

Final project for a python course. This project is meant to allow workers/volunteers at a small-scale [library of things](https://en.wikipedia.org/wiki/Library_of_things) to keep track of items, people, item location, item ownership, and transactions. 'Ownership' can be kept track of so that people who want to share their possessions, but not give them up to the library (yet), can be eased into the initiative. 

- **library.db** is an SQL database and stores all the data.
- **interface.py** initialises an UI through which library workers can interact with the database without ever typing SQL code.

These are the only two files required to run this application. They need to be in the same folder. **schema.sql** is a copy of the SQL code used to initialise the database file, in case the original file gets lost or a techy person needs a quick overview of its structure. This is all meant to work on a single computer—no way to edit the same database from two different computers. It is reccommended the library keeps at least one up-to-date backup copy of library.db somewhere.

The database can store the following information:

- People:
	- Name (or pseudonym)
	- Contact information
	- Additional note
- Items:
	- Name
	- State (example: good / damaged / lost)
	- Additional note
	- Current owner
	- Current location (borrower)
 - History of edits

Through the UI, the worker can edit every item/person field mentioned above, on top of adding new items/people or deleting them. Each time one of these actions is taken, it is logged into a list the user can access via the main menu. Logs (the 'History of edits') are not editable nor deletable through the UI.

Additional notes:
- The lists of items and people can be filtered by typing into a search bar.
- The list of logs also has a search bar, which applies to the event description, but not its date.
- Out-of-the-box, the database is empty except for one ‘person’: **.LIBRARY (ID: 1)**. This is meant to represent the library itself. Items ‘borrowed’ by .LIBRARY should be the ones currently in stock. .LIBRARY cannot be deleted through the UI, but its fields can be edited.
- Deleted items / people are not actually deleted from the database, but their fields emptied out and their name changed to 'DELETED ITEM / PERSON'. Reason: sloppy solution to avoid issues with the UI and objects sometimes having the same ID as a deleted object. :/
