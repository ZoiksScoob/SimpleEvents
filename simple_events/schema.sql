DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS event;
DROP TABLE IF EXISTS ticket;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  CONSTRAINT uq_user_username UNIQUE (username)
);

CREATE TABLE event (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    date DATE NOT NULL,
    initial_number_of_tickets INTEGER NOT NULL,
    additional_number_of_tickets INTEGER NULL,
    guid BLOB NOT NULL,
    date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    author_id INTEGER NOT NULL,
    FOREIGN KEY (author_id) REFERENCES user (id),
    CONSTRAINT uq_event_guid UNIQUE (guid)
);

CREATE TABLE ticket (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guid BLOB NOT NULL,
    is_redeemed BIT NOT NULL DEFAULT 0,
    event_id INTEGER NOT NULL,
    date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    author_id INTEGER NOT NULL,
    FOREIGN KEY (author_id) REFERENCES user (id)
    FOREIGN KEY (event_id) REFERENCES event (id),
    CONSTRAINT uq_ticket_guid UNIQUE (guid)
);
