import tempfile
import unittest
from pathlib import Path

import database
from views import render_page


class ViewsTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_database_path = database.DATABASE_PATH
        database.DATABASE_PATH = Path(self.temp_dir.name) / "test_denari.db"
        database.initialize_database()

    def tearDown(self):
        database.DATABASE_PATH = self.original_database_path
        self.temp_dir.cleanup()

    def test_render_page_shows_default_group_and_empty_table(self):
        html = render_page()

        self.assertIn("<h1>Denari</h1>", html)
        self.assertIn("General (open)", html)
        self.assertIn("No expenses yet.", html)

    def test_render_page_escapes_user_visible_values(self):
        html = render_page(
            error="<bad>",
            values={
                "expense_name": '<script>alert("x")</script>',
                "amount": "10",
                "paid_by": "Neha",
            },
        )

        self.assertIn("&lt;bad&gt;", html)
        self.assertIn("&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;", html)
        self.assertNotIn('<script>alert("x")</script>', html)


if __name__ == "__main__":
    unittest.main()
