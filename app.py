import logging
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

from database import (
    close_group,
    create_group,
    get_group,
    initialize_database,
    mark_expense_settled,
    save_expense,
)
from expenses import parse_expense_fields, split_expense, validate_expense
from views import get_selected_group_id, render_page

logger = logging.getLogger(__name__)
HOME_IMAGE_PATH = Path(__file__).with_name("IMG-20250412-WA0240.jpg")


class DenariHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path == "/home-image":
            self.serve_home_image()
            return

        query = parse_qs(parsed_url.query)
        result = query.get("message", [""])[0].strip() or None
        self.send_html(
            result=result,
            selected_group_id=self.get_selected_group_id(query),
        )

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        form_data = self.rfile.read(content_length).decode("utf-8")
        fields = parse_qs(form_data)
        action = fields.get("action", ["add_expense"])[0]

        if action == "create_group":
            self.handle_create_group(fields)
            return

        if action == "close_group":
            self.handle_close_group(fields)
            return

        if action == "settle_expense":
            self.handle_settle_expense(fields)
            return

        self.handle_add_expense(fields)

    def handle_add_expense(self, fields):
        selected_group_id = self.get_selected_group_id(fields)
        selected_group = get_group(selected_group_id) if selected_group_id else None
        parsed_fields = parse_expense_fields(fields)
        amount, error = validate_expense(
            parsed_fields["expense_name"],
            parsed_fields["amount_text"],
            parsed_fields["paid_by"],
            selected_group,
        )

        if error is None:
            split = split_expense(
                parsed_fields["expense_name"],
                amount,
                parsed_fields["paid_by"],
            )
            expense_id = save_expense(
                group_id=selected_group_id,
                **split_without_message(split),
            )
            log_saved_expense(expense_id, selected_group_id, split)
            self.redirect_to_group(selected_group_id, split["message"])
            return

        self.send_html(
            error=error,
            values={
                "expense_name": parsed_fields["expense_name"],
                "amount": parsed_fields["amount_text"],
                "paid_by": parsed_fields["paid_by"],
            },
            selected_group_id=selected_group_id,
        )

    def handle_create_group(self, fields):
        group_name = fields.get("group_name", [""])[0].strip()
        if not group_name:
            self.send_html(error="Enter a group name.")
            return

        group_id = create_group(group_name)
        logger.info("created expense group id=%s name=%s", group_id, group_name)
        self.redirect_to_group(group_id, f"Created expense group {group_name}.")

    def handle_close_group(self, fields):
        selected_group_id = self.get_selected_group_id(fields)
        selected_group = get_group(selected_group_id) if selected_group_id else None

        if selected_group is None:
            self.send_html(error="Could not find that group.")
            return

        updated_count = close_group(selected_group_id)
        if updated_count:
            logger.info("closed expense group id=%s", selected_group_id)
            self.redirect_to_group(
                selected_group_id,
                f"Closed {selected_group['name']} and marked its expenses settled.",
            )
        else:
            self.send_html(error="Could not close that group.")

    def handle_settle_expense(self, fields):
        selected_group_id = self.get_selected_group_id(fields)
        expense_id_text = fields.get("expense_id", [""])[0].strip()

        try:
            expense_id = int(expense_id_text)
        except ValueError:
            self.send_html(
                error="Could not mark expense as settled.",
                selected_group_id=selected_group_id,
            )
            return

        updated_count = mark_expense_settled(expense_id, selected_group_id)
        if updated_count:
            logger.info("marked expense id=%s as settled", expense_id)
            self.redirect_to_group(selected_group_id, "Expense marked as settled.")
        else:
            self.send_html(
                error="Could not find that expense.",
                selected_group_id=selected_group_id,
            )

    def send_html(self, result=None, error=None, values=None, selected_group_id=None):
        html = render_page(
            result=result,
            error=error,
            values=values,
            selected_group_id=selected_group_id,
        )
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def serve_home_image(self):
        if not HOME_IMAGE_PATH.exists():
            self.send_error(404, "Home image not found")
            return

        body = HOME_IMAGE_PATH.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "image/jpeg")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def redirect_to_group(self, group_id, message):
        query = urlencode({
            "group_id": group_id,
            "message": message,
        })
        self.send_response(303)
        self.send_header("Location", f"/?{query}")
        self.end_headers()

    def get_selected_group_id(self, fields):
        group_id = fields.get("group_id", [""])[0]
        return get_selected_group_id(group_id)


def split_without_message(split):
    return {
        "expense_name": split["expense_name"],
        "amount": split["amount"],
        "paid_by": split["paid_by"],
        "owed_by": split["owed_by"],
        "owed_to": split["owed_to"],
        "owed_amount": split["owed_amount"],
    }


def log_saved_expense(expense_id, group_id, split):
    logger.info(
        "saved expense id=%s group_id=%s name=%s amount=%.2f paid_by=%s",
        expense_id,
        group_id,
        split["expense_name"],
        split["amount"],
        split["paid_by"],
    )


def get_server_address():
    port = int(os.environ.get("PORT", "8000"))
    host = "0.0.0.0" if "PORT" in os.environ else "127.0.0.1"
    return host, port


def run(host=None, port=None):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    if host is None or port is None:
        default_host, default_port = get_server_address()
        host = host or default_host
        port = port or default_port

    initialize_database()
    logger.info("database initialized at denari.db")
    server = HTTPServer((host, port), DenariHandler)
    logger.info("denari server started at http://%s:%s", host, port)
    server.serve_forever()


if __name__ == "__main__":
    run()
