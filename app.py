"""Blogly application."""

from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, request, redirect, render_template, flash
from models import db, connect_db, User, Post

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
connect_db(app)

app.config['SECRET_KEY'] = "SECRET!"
debug = DebugToolbarExtension(app)


db.create_all()


@app.route("/")
def redirect_to_users_list():
    """ For now, redirects to a list of users. """
    return redirect("/users")


@app.route("/users")
def show_users_list():
    """ Shows all users with a link to the user's detail page. """
    return render_template("user_listing.html", users=User.query.all())


@app.route("/users/new")
def show_create_user_page():
    """ Shows create user form page. """
    return render_template("new_user.html", user="")


@app.route("/users/new", methods=["POST"])
def save_new_user_then_redirect():
    """ Handles create new user form submission,
    saves that new user to the database,
    then redirects to /users. """
    first_name, last_name, image_url = get_user_data(request.form)
    # save to database

    if first_name is None:
        flash('The first name is required')
        return redirect("/users/new")

    new_user = User(
        first_name=first_name,
        last_name=last_name,
        image_url=image_url)
    db.session.add(new_user)
    db.session.commit()
    # redirect to all users list
    return redirect("/users")


@app.route("/users/<int:user_id>")
def show_user_details(user_id):
    """ Shows information about a user. """
    user = User.query.get_or_404(user_id)
    posts = user.posts
    return render_template("user_detail.html", user=user, posts=posts)


@app.route("/users/<int:user_id>/edit")
def show_user_edit_form(user_id):
    """ Shows the user edit page for a given User id. """
    user = User.query.get_or_404(user_id)
    return render_template("user_edit.html", user=user)


@app.route("/users/<int:user_id>/edit", methods=["POST"])
def save_user_edits_then_redirect(user_id):
    """ Saves user edits into the database,
    then redirects to users list. """
    user = User.query.get_or_404(user_id)
    user.first_name, user.last_name, user.image_url = get_user_data(
        request.form)

    if user.first_name is None:
        flash('The first name is required')
        return redirect(f"/users/{user_id}/edit")

    db.session.commit()
    return redirect("/users")


@app.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user_then_redirect(user_id):
    """ Deletes the user for the given id,
    then redirects to users list. """
    user = User.query.get_or_404(user_id)
    if user.posts:
        flash("Cannot delete user with posts.")
        return redirect(f"/users/{user_id}")
    db.session.delete(user)
    db.session.commit()
    return redirect("/users")


@app.route("/users/<int:user_id>/posts/new")
def show_new_post_form(user_id):
    """ Shows the form for new posts """
    user = User.query.get_or_404(user_id)

    return render_template('new_post.html',
                           user=user,
                           post={"title": "", "content": ""})


@app.route("/users/<int:user_id>/posts/new", methods=["POST"])
def save_new_post_then_redirect(user_id):
    """ Save new post then redirect
        to user details page """
    user = User.query.get_or_404(user_id)

    post_title, post_content = get_post_data(request.form)

    if None in (post_title, post_content):
        flash("Posts must have both: title and content")
        return redirect(f'/users/{user_id}/posts/new')
    post = Post(title=post_title, content=post_content, user_id=user_id)

    db.session.add(post)
    db.session.commit()

    return redirect(f"/users/{user_id}")


@app.route("/posts/<int:post_id>")
def show_post_details(post_id):
    """ Shows the details about the post """
    post = Post.query.get_or_404(post_id)
    user = User.query.get_or_404(post.user_id)
    return render_template("post_detail.html", post=post, user=user)


@app.route("/posts/<int:post_id>/edit")
def show_post_edit_form(post_id):
    """ Shows the edit form for the posts """
    post = Post.query.get_or_404(post_id)
    user = User.query.get_or_404(post.user_id)

    return render_template("post_edit.html", post=post, user=user)


@app.route("/posts/<int:post_id>/edit", methods=['POST'])
def save_post_edits_then_redirect(post_id):
    """ Edits the post then redirect to post details """
    post = Post.query.get_or_404(post_id)

    post.title, post.content = get_post_data(request.form)

    if None in (post.title, post.content):
        flash("Posts must have a title and content")
        return redirect(f'/posts/{post_id}/edit')

    db.session.commit()

    return redirect(f"/posts/{post_id}")


@app.route("/posts/<int:post_id>/delete", methods=['POST'])
def delete_post_then_redirect(post_id):
    """ Delete the post then redirect to the user details """
    post = Post.query.get_or_404(post_id)
    user_id = post.user_id

    db.session.delete(post)
    db.session.commit()

    return redirect(f"/users/{user_id}")


def get_user_data(user_data):
    """ Grab user form data and return as a list. """
    first_name = user_data.get('first_name')
    first_name = first_name if first_name else None

    last_name = user_data.get('last_name')

    profile_img = user_data.get('img_url')
    profile_img = profile_img if profile_img else "/static/default_profile.jpg"

    return [first_name,
            last_name,
            profile_img]


def get_post_data(post_data):
    """ Grab post form data and return as a list. """
    post_title = post_data.get('post_title')
    post_title = post_title if post_title else None

    post_content = post_data.get('post_content')
    post_content = post_content if post_content else None

    return [post_title,
            post_content]
