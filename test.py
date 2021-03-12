from app import app
import unittest

class FlaskTestCase(unittest.TestCase):

    # opens up the team logon Route
    def test_1_team_login(self):
        tester = app.test_client(self)
        response = tester.get("/", content_type = "html/text")
        self.assertEqual(response.status_code, 200)

    




if __name__ == "__main__":
    unittest.main()