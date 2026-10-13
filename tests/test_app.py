import os
import unittest

from app import create_app


class AppConfigSmokeTest(unittest.TestCase):
    def test_app_creates_with_sqlite_default(self):
        os.environ.pop("DATABASE_URL", None)
        app = create_app()
        self.assertIn("sqlite", app.config["SQLALCHEMY_DATABASE_URI"])


if __name__ == "__main__":
    unittest.main()
