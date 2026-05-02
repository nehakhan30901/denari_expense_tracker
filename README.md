# denari

A basic Python expense tracker for Neha and Stephen.

## Run

```sh
python3 app.py
```

Then open:

```text
http://localhost:8000
```

Create an expense group, then enter an expense name, amount, and who paid.
Denari splits the expense evenly and shows who owes whom for that group.
Submitted expenses are stored in `denari.db`.

The home page shows the selected group's expenses in a table and the current
balance for that group. Mark an individual expense as settled to exclude it from
the current balance, or close the group to mark all of its expenses settled.

## Test

```sh
python3 -m unittest discover -s tests
```

## Render

Use this start command:

```sh
python3 app.py
```

Denari reads Render's `PORT` environment variable and binds to `0.0.0.0`
automatically when `PORT` is present.

For persistent SQLite storage on Render:

1. Add a persistent disk mounted at:

```text
/var/data
```

2. Add this environment variable:

```text
DATABASE_PATH=/var/data/denari.db
```

SQLite creates `denari.db` automatically on first startup.
