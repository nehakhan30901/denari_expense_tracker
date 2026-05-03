# denari

A basic Python expense tracker for Neha and Stephen.

## Run

Local-only:

```sh
python3 app.py
```

Then open:

```text
http://localhost:8000
```

Wi-Fi accessible from another device on the same network:

```sh
PORT=8000 python3 app.py
```

Then open:

```text
http://<mac-wifi-ip>:8000
```

Create an expense group, then enter an expense name, amount, and who paid.
Denari splits the expense evenly and shows who owes whom for that group.
Submitted expenses are stored in `denari.db`.

The home page shows the selected group's expenses in a table and the current
balance for that group. Mark an individual expense as settled to exclude it from
the current balance, or close the group to mark all of its expenses settled.

Expense data is stored locally in:

```text
denari.db
```

Keep this file to preserve production data.

## Test

```sh
python3 -m unittest discover -s tests
```
