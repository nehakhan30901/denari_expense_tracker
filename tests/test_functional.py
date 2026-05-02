import http.client
import tempfile
import threading
import unittest
from http.server import HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import app
import database


class FunctionalTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_database_path = database.DATABASE_PATH
        self.original_home_image_path = app.HOME_IMAGE_PATH
        database.DATABASE_PATH = Path(self.temp_dir.name) / "test_denari.db"
        app.HOME_IMAGE_PATH = Path(self.temp_dir.name) / "home.jpg"
        app.HOME_IMAGE_PATH.write_bytes(b"fake jpeg bytes")
        database.initialize_database()

        self.server = HTTPServer(("127.0.0.1", 0), app.DenariHandler)
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()
        self.base_host = "127.0.0.1"
        self.base_port = self.server.server_address[1]

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        database.DATABASE_PATH = self.original_database_path
        app.HOME_IMAGE_PATH = self.original_home_image_path
        self.temp_dir.cleanup()

    def request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection(self.base_host, self.base_port)
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        response_body = response.read()
        connection.close()
        return response, response_body

    def post_form(self, fields):
        body = "&".join(f"{key}={value}" for key, value in fields.items())
        return self.request(
            "POST",
            "/",
            body=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    def test_home_page_renders_group_controls_and_image(self):
        response, body = self.request("GET", "/")
        html = body.decode("utf-8")

        self.assertEqual(200, response.status)
        self.assertIn("<h1>Denari</h1>", html)
        self.assertIn('src="/home-image"', html)
        self.assertIn("Expense group", html)
        self.assertIn("No expenses yet.", html)

    def test_home_image_is_served(self):
        response, body = self.request("GET", "/home-image")

        self.assertEqual(200, response.status)
        self.assertEqual("image/jpeg", response.getheader("Content-Type"))
        self.assertEqual(b"fake jpeg bytes", body)

    def test_create_group_redirects_to_new_group(self):
        response, _ = self.post_form({
            "action": "create_group",
            "group_name": "Alaska",
        })

        self.assertEqual(303, response.status)
        location = response.getheader("Location")
        query = parse_qs(urlparse(location).query)
        group_id = int(query["group_id"][0])
        self.assertEqual("Alaska", database.get_group(group_id)["name"])

    def test_add_expense_redirects_clears_form_and_saves_expense(self):
        group_id = database.create_group("Alaska")
        response, _ = self.post_form({
            "action": "add_expense",
            "group_id": group_id,
            "expense_name": "Flight",
            "amount": "1000",
            "paid_by": "Stephen",
        })

        self.assertEqual(303, response.status)
        self.assertIn("group_id=", response.getheader("Location"))

        expenses = database.list_expenses(group_id)
        self.assertEqual(1, len(expenses))
        self.assertEqual("Flight", expenses[0]["expense_name"])
        self.assertEqual("Neha", expenses[0]["owed_by"])
        self.assertEqual(500, expenses[0]["owed_amount"])

        page_response, page_body = self.request("GET", f"/?group_id={group_id}")
        html = page_body.decode("utf-8")
        self.assertEqual(200, page_response.status)
        self.assertIn('value=""  required', html)
        self.assertIn("Neha owes Stephen $500.00 for this group.", html)

    def test_invalid_expense_does_not_save(self):
        group_id = database.create_group("Alaska")
        response, body = self.post_form({
            "action": "add_expense",
            "group_id": group_id,
            "expense_name": "Flight",
            "amount": "-10",
            "paid_by": "Stephen",
        })

        self.assertEqual(200, response.status)
        self.assertIn("Enter a valid amount greater than 0.", body.decode("utf-8"))
        self.assertEqual([], database.list_expenses(group_id))

    def test_close_group_settles_all_expenses_and_zeroes_balance(self):
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

        response, _ = self.post_form({
            "action": "close_group",
            "group_id": group_id,
        })

        self.assertEqual(303, response.status)
        self.assertEqual(1, database.get_group(group_id)["closed"])
        self.assertEqual(1, database.list_expenses(group_id)[0]["settled"])
        self.assertEqual(0, database.get_balance(group_id))


if __name__ == "__main__":
    unittest.main()
