PEOPLE = {"Neha", "Stephen"}


def parse_expense_fields(fields):
    return {
        "expense_name": fields.get("expense_name", [""])[0].strip(),
        "amount_text": fields.get("amount", [""])[0].strip(),
        "paid_by": fields.get("paid_by", [""])[0].strip(),
    }


def validate_expense(expense_name, amount_text, paid_by, selected_group):
    try:
        amount = float(amount_text)
        if amount <= 0:
            raise ValueError
    except ValueError:
        return None, "Enter a valid amount greater than 0."

    if not expense_name:
        return None, "Enter an expense name."

    if paid_by not in PEOPLE:
        return None, "Choose who paid."

    if selected_group is None:
        return None, "Create an expense group first."

    if selected_group["closed"]:
        return None, "This group is closed. Create a new group to add expenses."

    return amount, None


def split_expense(expense_name, amount, paid_by):
    owed_amount = amount / 2
    if paid_by == "Neha":
        owed_by = "Stephen"
        owed_to = "Neha"
    else:
        owed_by = "Neha"
        owed_to = "Stephen"

    return {
        "expense_name": expense_name,
        "amount": amount,
        "paid_by": paid_by,
        "owed_by": owed_by,
        "owed_to": owed_to,
        "owed_amount": owed_amount,
        "message": f"{owed_by} owes {owed_to} ${owed_amount:.2f} for {expense_name}",
    }
