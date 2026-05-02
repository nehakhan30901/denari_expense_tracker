import os
import unittest
from unittest.mock import patch

import app


class AppTestCase(unittest.TestCase):
    def test_get_server_address_defaults_to_localhost(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(("127.0.0.1", 8000), app.get_server_address())

    def test_get_server_address_uses_render_port(self):
        with patch.dict(os.environ, {"PORT": "10000"}, clear=True):
            self.assertEqual(("0.0.0.0", 10000), app.get_server_address())


if __name__ == "__main__":
    unittest.main()
