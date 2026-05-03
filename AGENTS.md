# Denari Agent Notes

Denari is a local Python expense tracker for Neha and Stephen.

## Run

Local-only:

```sh
python3 app.py
```

Wi-Fi accessible:

```sh
PORT=8000 python3 app.py
```

Open:

```text
http://localhost:8000
http://<mac-wifi-ip>:8000
```

## Test

```sh
python3 -m unittest discover -s tests
```

## Architecture

- `app.py`: HTTP routing and response coordination.
- `database.py`: SQLite schema, migrations, and queries.
- `expenses.py`: expense validation and split/full-amount calculation.
- `views.py`: HTML rendering helpers.
- `templates.py`: main HTML/CSS template.
- `tests/`: unit and functional tests.

## Product Rules

- Expense groups represent trips or contexts, like Alaska or Italy.
- Each expense belongs to one group.
- Expenses can be split evenly or marked as full amount owed by the other person.
- If `Split evenly` is checked, owed amount is `amount / 2`.
- If `Split evenly` is unchecked, owed amount is the full amount.
- The payer is owed by the other person.
- Individual expenses can be marked settled.
- Closing a group marks all expenses in that group settled.
- Balances only count unsettled expenses.

## Database

Default local database:

```text
denari.db
```

Optional persistent path:

```sh
DATABASE_PATH=/var/data/denari.db
```

SQLite creates the file automatically on first startup.

## Git

Run tests before committing.
