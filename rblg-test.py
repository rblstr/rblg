import os
import tempfile
import hmac
import unittest
import rblg


class FrontPageTestCase(unittest.TestCase):
    def setUp(self):
        rblg.app.testing = True
        self.app = rblg.app.test_client()
        rblg.db.create_all()

    def tearDown(self):
        """ Cleanup database file """
        rblg.db.session.remove()
        rblg.db.drop_all()

    def test_frontpage(self):
        """ make sure everything is setup correctly """
        response = self.app.get('/', content_type='text/html')
        self.assertEqual(response.status_code, 200)

    def test_db(self):
        """ make sure database file exists """
        self.assertTrue(os.path.exists('rblg.db'))


class UserLoginTestCase(unittest.TestCase):
    def setUp(self):
        """ Setup empty database """
        rblg.app.testing = True
        self.app = rblg.app.test_client()
        rblg.db.create_all()
        test_user = rblg.User('admin', 'admin')
        rblg.db.session.add(test_user)
        rblg.db.session.commit()

    def tearDown(self):
        """ Cleanup database file """
        rblg.db.session.remove()
        rblg.db.drop_all()

    def login(self, username, password):
        """ login helper """
        return self.app.post('/login', data={
                'username':username,
                'password':password
            }, follow_redirects=True)

    def logout(self):
        """ logout helper """
        return self.app.get('/logout', follow_redirects=True)

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
        response = self.app.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Logout successful' in response.data)
        response = self.app.get('/')
        self.assertFalse('/logout' in response.data)
        self.assertTrue('/login' in response.data)


class PostsTestCase(unittest.TestCase):
    def setUp(self):
        """ Setup empty database """
        rblg.app.testing = True
        self.app = rblg.app.test_client()
        rblg.db.create_all()
        test_user = rblg.User('admin', 'admin')
        rblg.db.session.add(test_user)
        rblg.db.session.commit()

    def tearDown(self):
        """ Cleanup database file """
        rblg.db.session.remove()
        rblg.db.drop_all()

    def test_empty_db(self):
        """ database is blank """
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('No entries' in response.data)

    def test_must_login_to_post(self):
        """ must login to post """
        response = self.app.post('/blogs', data={
            'title':'post_id_1',
            'content':'post_id_1_content'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Must be logged in to post' in response.data)

    def test_login_and_post(self):
        """ can only create posts when logged in """
        response = self.app.post('/login', data={
            'username':'admin',
            'password':'admin'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Login successful' in response.data)
        response = self.app.post('/blogs', data={
            'title':'post_id_1',
            'content':'post_id_1_content'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Post created' in response.data)

    def test_login_and_post_content_error(self):
        """ can only create posts when logged in """
        response = self.app.post('/login', data={
            'username':'admin',
            'password':'admin'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Login successful' in response.data)
        response = self.app.post('/blogs', data={
            'title':'post_id_1',
            'content':''
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('No content' in response.data)

    def test_login_and_post_title_error(self):
        """ can only create posts when logged in """
        response = self.app.post('/login', data={
            'username':'admin',
            'password':'admin'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Login successful' in response.data)
        response = self.app.post('/blogs', data={
            'title':'',
            'content':'post_id_1_content'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('No title' in response.data)

    def test_post_added_to_db(self):
        """ can only create posts when logged in """
        response = self.app.post('/login', data={
            'username':'admin',
            'password':'admin'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Login successful' in response.data)
        response = self.app.post('/blogs', data={
            'title':'post_id_1',
            'content':'post_id_1_content'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Post created' in response.data)
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('post_id_1' in response.data)
        self.assertTrue('post_id_1_content' in response.data)

class UserRegistrationTestCase(unittest.TestCase):
    def setUp(self):
        rblg.app.testing = True
        self.app = rblg.app.test_client()
        rblg.db.create_all()

    def tearDown(self):
        """ Cleanup database file """
        rblg.db.session.remove()
        rblg.db.drop_all()

    def test_registration_exists(self):
        """ Test registration URL """
        response = self.app.post('/register', data={
            'username':'test_username',
            'password':'test_password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Registration successful' in response.data)

    def test_register_username_error(self):
        """ An error is reported when an invalid username is entered """
        response = self.app.post('/register', data={
            'username':'',
            'password':'password'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Invalid username' in response.data)

    def test_register_password_error(self):
        """ An error is reported when an invalid password is entered """
        response = self.app.post('/register', data={
            'username':'test_username',
            'password':''
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Invalid password' in response.data)

    def test_login_after_register(self):
        """ Test if logged in after registration """
        self.test_registration_exists()
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('/logout' in response.data)

    def test_register_logout_login(self):
        """ Test if we can re-login after registration """
        self.test_login_after_register()
        response = self.app.post('/login', data={
            'username':'test_username',
            'password':'test_password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Login successful' in response.data)


class CookieTestCase(unittest.TestCase):
    def test_create_secure_cookie(self):
        cookie = rblg.create_cookie('admin')
        self.assertEqual(cookie, "%s|%s" % ('admin', hmac.new('skeleton_key', 'admin').hexdigest()))

    def test_created_cookies_can_be_validated(self):
        cookie = rblg.create_cookie('admin')
        self.assertTrue(rblg.validate_cookie(cookie))

    def test_tampered_cookies_fail_validation_username(self):
        cookie = rblg.create_cookie('admin')
        split = cookie.split('|')
        new_cookie = 'new_username|%s' % split[1]
        self.assertFalse(rblg.validate_cookie(new_cookie))

    def test_tampered_cookies_fail_validation_hash(self):
        cookie = '%s|%s' % ('username', hmac.new('my_key', 'username').hexdigest())
        self.assertFalse(rblg.validate_cookie(cookie))

    def test_non_cookie_fails_validation(self):
        cookie = 'i_am_not_a_cookie'
        self.assertFalse(rblg.validate_cookie(cookie))

    def test_parse_cookie(self):
        cookie = rblg.create_cookie('username')
        self.assertEqual('username', rblg.parse_cookie(cookie))


if __name__ == '__main__':
    unittest.main()

