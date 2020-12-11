from unittest import TestCase
from app import app
from models import db, User, Post

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
        Post.query.delete()
        User.query.delete()

        test_user = User(first_name="Tony",
                         last_name="Stark",
                         image_url="https://m.hindustantimes.com/rf/image_size_1200x900/HT/p2/2019/08/12/Pictures/_ca1ae8d6-bcf4-11e9-9bc9-c6f10a5dc6e3.jpg")
        db.session.add(test_user)
        db.session.commit()

        test_post = Post(user_id=test_user.id, title="Thanos Sucks", content="*Snap*")
        db.session.add(test_post)

        test_post2 = Post(user_id=test_user.id,
                          title="Thanks from Stark Industries",
                          content="We thank you for blahblahblahblahalblahh")
        db.session.add(test_post2)

        db.session.commit()

        self.test_user_id = test_user.id
        self.test_post = test_post
        self.test_post2 = test_post2

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
            response = client.get(f'/users/{self.test_user_id}')
            html = response.get_data(as_text=True)
            self.assertIn("Tony Stark", html)

    def test_user_edit_form(self):
        """ Test that user edit form shows the
            first and last  name of the user"""
        with app.test_client() as client:
            response = client.get(f'/users/{self.test_user_id}/edit')
            html = response.get_data(as_text=True)
            self.assertIn('value="Tony"', html)
            self.assertIn('value="Stark"', html)

    def test_new_post_form(self):
        """ Tests whether the new post form appears correctly  """
        with app.test_client() as client:
            response = client.get(f'/users/{self.test_user_id}/posts/new')

            html = response.get_data(as_text=True)
            self.assertIn('Add post for Tony Stark', html)
            self.assertIn('post_title', html)
            self.assertIn('post_content', html)

    def test_post_create(self):
        """ Tests the creation of a post """
        with app.test_client() as client:
            response = client.post(f'/users/{self.test_user_id}/posts/new',
                                   data={
                                       'post_title': 'Created by unittest',
                                       'post_content': """This post was
                                       created for testing a flask app."""
                                   },
                                   follow_redirects=True)

            html = response.get_data(as_text=True)

            self.assertIn('Created by unittest', html)
            self.assertIn('Tony Stark', html)

    def test_post_edit(self):
        """ Tests the editing of a post """
        with app.test_client() as client:
            response = client.post(f'/posts/{self.test_post2.id}/edit',
                                   data={
                                       'post_title': 'Edited by unittest',
                                       'post_content': """This post was
                                       EDITED for testing a flask app."""
                                   },
                                   follow_redirects=True)

            html = response.get_data(as_text=True)

            self.assertIn('Edited by unittest', html)
            self.assertIn('Tony Stark', html)
