"""Blogly application."""

from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, request, redirect, render_template, flash
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Post, Tag

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
    flash(f"Deleted user: {user.first_name} {user.last_name}")

    db.session.delete(user)
    db.session.commit()
    return redirect("/users")


########## Post Routes ##########

@app.route("/users/<int:user_id>/posts/new")
def show_new_post_form(user_id):
    """ Shows the form for new posts """
    user = User.query.get_or_404(user_id)

    return render_template('new_post.html',
                           user=user,
                           post={"title": "", "content": "", "tags":[]},
                           tags=Tag.query.all())


@app.route("/users/<int:user_id>/posts/new", methods=["POST"])
def save_new_post_then_redirect(user_id):
    """ Save new post then redirect
        to user details page """
    User.query.get_or_404(user_id)

    post_title, post_content, tag_list = get_post_data(request.form)

    if None in (post_title, post_content):
        flash("Posts must have both: title and content")
        return redirect(f'/users/{user_id}/posts/new')

    post = Post(title=post_title, content=post_content, user_id=user_id)
    db.session.add(post)
    db.session.commit()

    if tag_list is not None:
        post.tags = [Tag.query.filter_by(name=tag_name) for tag_name in tag_list]

    db.session.commit()
    return redirect(f"/users/{user_id}")


@app.route("/posts/<int:post_id>")
def show_post_details(post_id):
    """ Shows the details about the post """
    post = Post.query.get_or_404(post_id)
    return render_template("post_detail.html", post=post, tags=post.tags)


@app.route("/posts/<int:post_id>/edit")
def show_post_edit_form(post_id):
    """ Shows the edit form for the posts """
    post = Post.query.get_or_404(post_id)
    return render_template("post_edit.html", post=post, tags=Tag.query.all())


@app.route("/posts/<int:post_id>/edit", methods=['POST'])
def save_post_edits_then_redirect(post_id):
    """ Edits the post then redirect to post details """
    post = Post.query.get_or_404(post_id)

    post.title, post.content, tag_list = get_post_data(request.form)
    print("Tag_list=", tag_list)

    if None in (post.title, post.content):
        flash("Posts must have a title and content")
        return redirect(f'/posts/{post_id}/edit')

    db.session.commit()

    # Loop through the tag_list
    # Check if any of the tags have been unchecked
    # Find the instance of the tag
    # Check whether its already in the post.tags
    # If not append the tag instance to post.tags
    # post.tags.append(OUR TAG INSTANCE)

    if tag_list is not None:
        post.tags = [Tag.query.filter_by(name=tag_name).one() for tag_name in tag_list]

    db.session.commit()

    return redirect(f"/posts/{post_id}")


@app.route("/posts/<int:post_id>/delete", methods=['POST'])
def delete_post_then_redirect(post_id):
    """ Delete the post then redirect to the user details """
    post = Post.query.get_or_404(post_id)
    flash(f"Deleted Post: {post.title}")
    db.session.delete(post)
    db.session.commit()

    return redirect(f"/users/{post.user_id}")

########## Tag Routing ##########


@app.route("/tags")
def show_tag_list():
    """ Shows list of all tags """
    tags = Tag.query.all()
    return render_template("tag_listing.html", tags=tags)


@app.route("/tags/<int:tag_id>")
def show_tag_details(tag_id):
    """ Shows the details about the tag """
    tag = Tag.query.get_or_404(tag_id)
    return render_template("tag_detail.html", tag=tag)


@app.route("/tags/new")
def show_new_tag_form():
    """ Shows the tag creation form """
    return render_template("new_tag.html")


@app.route("/tags/new", methods=["POST"])
def save_new_tag_then_redirect():
    """ Saves a new tag then redirects
        to the tags list """
    tag_name = get_tag_data(request.form)

    if tag_name is None:
        flash("Cannot create empty tag. ")
        return redirect("/tags/{tag_id}/edit")

    # Tried to filter out duplicate tags but didnt work
    # if Tag.query.filter(Tag.name==tag_name):
    #     flash("Cannot create duplicate tag.")
    #     return redirect("/tags/new")

    tag = Tag(name=tag_name)
    db.session.add(tag)

    try:
        db.session.commit()
    except db.IntegrityError:
        db.session.rollback()
        flash('Cannot create a duplicate tag.')
        return redirect("/tags/new")

    return redirect("/tags")


@app.route("/tags/<int:tag_id>/edit")
def show_edit_tag_form(tag_id):
    """ Shows edit tag form """
    tag = Tag.query.get_or_404(tag_id)
    return render_template("tag_edit.html", tag=tag)


@app.route("/tags/<int:tag_id>/edit", methods=["POST"])
def save_tag_edits_then_redirect(tag_id):
    """ Shows the details about the post """
    tag = Tag.query.get_or_404(tag_id)

    tag_name = get_tag_data(request.form)
    if tag.name == tag_name:
        flash("No changes have been made.")
        return redirect(f"/tags/{tag_id}", tag=tag)

    if tag_name is None:
        flash("Cannot create empty tag. ")
        return redirect("/tags/{tag_id}/edit")

    # Tried to filter out duplicate tags but didnt work
    # if Tag.query.filter(Tag.name==tag_name):
    #     flash("Cannot create duplicate tag.")
    #     return redirect("/tags/new")

    tag.name = tag_name
    db.session.commit()
    return redirect(f"/tags/{tag_id}")


@app.route("/tags/<int:tag_id>/delete", methods=["POST"])
def delete_tag_then_redirect(tag_id):
    """ Deletes tag """
    tag = Tag.get_or_404(tag_id)
    flash(f"Deleted tag: {tag.name}")
    db.session.delete(tag)
    db.session.commit()
    return redirect("/tags")


########## Helper methods ##########
def get_user_data(user_data):
    """ Grab user form data and return as a list. """
    first_name = user_data.get('first_name') or None

    last_name = user_data.get('last_name')

    profile_img = user_data.get('img_url') or "/static/default_profile.jpg"

    return [first_name,
            last_name,
            profile_img]


def get_post_data(post_data):
    """ Grab post form data and return as a list. """
    post_title = post_data.get('post_title') or None
    post_content = post_data.get('post_content') or None
    tags = post_data.getlist('tags') or None

    return [post_title,
            post_content,
            tags]


def get_tag_data(tag_data):
    """ Grab tag form data and return. """
    return tag_data.get('tag_name') or None
