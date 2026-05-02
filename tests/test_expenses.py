import unittest

from expenses import parse_expense_fields, split_expense, validate_expense


class ExpensesTestCase(unittest.TestCase):
    def test_parse_expense_fields_strips_input_values(self):
        fields = {
            "expense_name": [" Flight "],
            "amount": [" 1000 "],
            "paid_by": ["Stephen"],
        }

        parsed = parse_expense_fields(fields)

        self.assertEqual("Flight", parsed["expense_name"])
        self.assertEqual("1000", parsed["amount_text"])
        self.assertEqual("Stephen", parsed["paid_by"])

    def test_validate_expense_rejects_invalid_amount(self):
        amount, error = validate_expense("Flight", "-10", "Stephen", {"closed": 0})

        self.assertIsNone(amount)
        self.assertEqual("Enter a valid amount greater than 0.", error)

    def test_validate_expense_rejects_closed_group(self):
        amount, error = validate_expense("Flight", "100", "Stephen", {"closed": 1})

        self.assertIsNone(amount)
        self.assertEqual("This group is closed. Create a new group to add expenses.", error)

    def test_split_expense_when_stephen_paid(self):
        split = split_expense("Flight", 1000, "Stephen")

        self.assertEqual("Neha", split["owed_by"])
        self.assertEqual("Stephen", split["owed_to"])
        self.assertEqual(500, split["owed_amount"])
        self.assertEqual("Neha owes Stephen $500.00 for Flight", split["message"])


if __name__ == "__main__":
    unittest.main()
