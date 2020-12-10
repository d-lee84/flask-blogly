from unittest import TestCase
from app import app
from models import db, User

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()

class BloglyTestCase(TestCase):

    def setUp(self):
        """Add test user."""

        User.query.delete()

        test_user = User(first_name="Tony", last_name="Hawk")
        db.session.add(test_user)
        db.session.commit()

        self.test_id = test_user.id

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

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

    def test_user_details(self):
        """ Test that user can be correctly created
            and displayed in the /users route"""
        with app.test_client() as client:
            response = client.get(f'/users/{self.test_id }')
            html = response.get_data(as_text=True)
            self.assertIn("Tony Hawk", html)

    def test_user_edit_form(self):
        """ Test that user edit form shows the 
            first and last  name of the user"""
        with app.test_client() as client:
            response = client.get(f'/users/{self.test_id }/edit')
            html = response.get_data(as_text=True)
            self.assertIn('value="Tony"', html)
            self.assertIn('value="Hawk"', html)


    # Test /users/edit, /users/delete
    # def test_user_edit(self):
    #     """ Test that user can be correctly created
    #         and displayed in the /users route"""
    #     with app.test_client() as client:
    #         response = client.get(f'/users/{self.test_id }')
    #         html = response.get_data(as_text=True)
    #         self.assertIn("Tony Hawk", html)
