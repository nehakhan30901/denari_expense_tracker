import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import database


class DatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_database_path = database.DATABASE_PATH
        database.DATABASE_PATH = Path(self.temp_dir.name) / "test_denari.db"
        database.initialize_database()

    def tearDown(self):
        database.DATABASE_PATH = self.original_database_path
        self.temp_dir.cleanup()

    def test_initialize_database_creates_default_group(self):
        groups = database.list_groups()

        self.assertEqual(1, len(groups))
        self.assertEqual("General", groups[0]["name"])
        self.assertEqual(0, groups[0]["closed"])

    def test_get_database_path_uses_environment_variable(self):
        custom_path = Path(self.temp_dir.name) / "custom" / "render.db"

        with patch.dict(os.environ, {"DATABASE_PATH": str(custom_path)}):
            self.assertEqual(custom_path, database.get_database_path())

    def test_get_connection_creates_parent_directory_for_database_path(self):
        custom_path = Path(self.temp_dir.name) / "nested" / "denari.db"

        with patch.dict(os.environ, {"DATABASE_PATH": str(custom_path)}):
            database.initialize_database()

        self.assertTrue(custom_path.exists())

    def test_save_expenses_and_calculate_group_balance(self):
        group_id = database.create_group("Alaska")

        database.save_expense(
            group_id=group_id,
            expense_name="Flight",
            amount=1000,
            paid_by="Stephen",
            owed_by="Neha",
            owed_to="Stephen",
            owed_amount=500,
            split_evenly=True,
        )
        database.save_expense(
            group_id=group_id,
            expense_name="Hotel",
            amount=600,
            paid_by="Neha",
            owed_by="Stephen",
            owed_to="Neha",
            owed_amount=300,
            split_evenly=False,
        )

        self.assertEqual(-200, database.get_balance(group_id))
        expenses = database.list_expenses(group_id)
        self.assertEqual(0, expenses[0]["split_evenly"])
        self.assertEqual(1, expenses[1]["split_evenly"])

    def test_mark_expense_settled_excludes_it_from_balance(self):
        group_id = database.create_group("Alaska")
        expense_id = database.save_expense(
            group_id=group_id,
            expense_name="Flight",
            amount=1000,
            paid_by="Stephen",
            owed_by="Neha",
            owed_to="Stephen",
            owed_amount=500,
        )

        updated_count = database.mark_expense_settled(expense_id, group_id)

        self.assertEqual(1, updated_count)
        self.assertEqual(0, database.get_balance(group_id))
        self.assertEqual(1, database.list_expenses(group_id)[0]["settled"])

    def test_close_group_marks_group_and_expenses_settled(self):
        group_id = database.create_group("Alaska")
        database.save_expense(
            group_id=group_id,
            expense_name="Flight",
            amount=1000,
            paid_by="Stephen",
            owed_by="Neha",
            owed_to="Stephen",
            owed_amount=500,
        )

        updated_count = database.close_group(group_id)

        self.assertEqual(1, updated_count)
        self.assertEqual(1, database.get_group(group_id)["closed"])
        self.assertEqual(1, database.list_expenses(group_id)[0]["settled"])
        self.assertEqual(0, database.get_balance(group_id))


if __name__ == "__main__":
    unittest.main()
