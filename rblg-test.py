import os
import tempfile
import unittest
import rblg


class FrontPageTestCase(unittest.TestCase):
    def setUp(self):
        rblg.app.testing = True
        self.app = rblg.app.test_client()

    def test_frontpage(self):
        """ make sure everything is setup correctly """
        response = self.app.get('/', content_type='text/html')
        self.assertEqual(response.status_code, 200)

    def test_db(self):
        """ make sure database file exists """
        self.assertTrue(os.path.exists('rblg.db'))


class RblgSetupTestCase(unittest.TestCase):
    def setUp(self):
        """ Setup empty database """
        self.db_file, rblg.app.config['DATABASE'] = tempfile.mkstemp()
        rblg.app.testing = True
        self.app = rblg.app.test_client()
        rblg.init_db()

    def tearDown(self):
        """ Cleanup database file """
        os.close(self.db_file)
        os.unlink(rblg.app.config['DATABASE'])

    def login(self, username, password):
        """ login helper """
        return self.app.post('/login', data={
                'username':username,
                'password':password
            })

    def logout(self):
        """ logout helper """
        return self.app.get('/logout')

    def test_empty_db(self):
        """ database is blank """
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('No entries' in response.data)

    def test_login_link(self):
        """ test login link is present when not logged in """
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('/login' in response.data)
        self.assertFalse('/logout' in response.data)

    def test_logout_link_after_login(self):
        """ test logout link is present after user logged in """
        response = self.login('admin', 'admin')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Login successful' in response.data)
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('/logout' in response.data)

    def test_error_login_username(self):
        """ pass invalid username """
        response = self.login('admin.x', 'admin')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Invalid username' in response.data)

    def test_error_login_password(self):
        """ pass invalid username """
        response = self.login('admin', 'admin.x')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Invalid password' in response.data)

    def test_login(self):
        """ login """
        response = self.login('admin', 'admin')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Login successful' in response.data)

    def test_logout(self):
        """ logout """
        response = self.logout()
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Logout successful' in response.data)

    def test_login_logout(self):
        """ logging out removes cookie and shows login form """
        response = self.login('admin', 'admin')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Login successful' in response.data)
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('/logout' in response.data)
        self.assertFalse('/login' in response.data)
        response = self.app.get('/logout')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Logout successful' in response.data)
        response = self.app.get('/')
        self.assertFalse('/logout' in response.data)
        self.assertTrue('/login' in response.data)


if __name__ == '__main__':
    unittest.main()
