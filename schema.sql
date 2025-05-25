CREATE TABLE people (
    id INTEGER,
    name TEXT,
    contact TEXT,
    note TEXT,
    PRIMARY KEY(id)
);
CREATE TABLE items (
    id INTEGER,
    name TEXT,
    state TEXT,
    note TEXT,
    PRIMARY KEY(id)
);
CREATE TABLE location (
    person_id INTEGER,
    item_id INTEGER,
    FOREIGN KEY(person_id) REFERENCES people(id),
    FOREIGN KEY(item_id) REFERENCES items(id)
);
CREATE TABLE ownership (
    person_id INTEGER,
    item_id INTEGER,
    FOREIGN KEY(person_id) REFERENCES people(id),
    FOREIGN KEY(item_id) REFERENCES items(id)
);
CREATE TABLE logs (
    id INTEGER,
    time TEXT,
    event TEXT,
    PRIMARY KEY(id)
);
INSERT INTO people (name, contact, note) VALUES(
    '.LIBRARY',
    'info@libraryofthings.org',
    'The object library itself.'
);
