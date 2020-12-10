from unittest import TestCase
from app import app


app.config['TESTING'] = True

app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']


class BloglyTestCase(TestCase):

    def test_root_redirect(self):
        """ Tests that root routes are redirected """
        with app.test_client() as client:
            resp = client.get("/")
   
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, "http://localhost/users")

    def test_root_follow_redirect(self):
        """ Tests that root route is redirected to /users """

        with app.test_client() as client:
            resp = client.get("/", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Users:", html)


    def test_users_page(self):
        """ Checks that users page contains list of users """
        with app.test_client() as client:
            resp = client.get("/users", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Users:", html)
            self.assertIn("<ul", html)
            self.assertIn("Add User", html)

# Test /users/edit, /users/delete

    def test_create_new_user_follow(self):
        """ Test that user can be correctly created
            and displayed in the /users route
        """
        with app.test_client() as client:
            resp = client.post('/users/new',
                               data={
                                   'first_name': 'Our',
                                   'last_name': 'Example'
                               },
                               follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertIn("Our", html)
            self.assertIn("Users:", html)
            self.assertIn("Example", html)
            self.assertIn("<li", html)


    # def test_(self):
    #     """ """
    #     with app.test_client() as client:

    # def test_(self):
    #     """ """
    #     with app.test_client() as client:
    