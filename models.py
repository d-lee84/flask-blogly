"""Models for Blogly."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """ Users in the blog website """

    __tablename__ = "users"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    first_name = db.Column(db.String(50),
                           nullable=False)
    last_name = db.Column(db.String(50),
                          nullable=False,
                          default='')
    image_url = db.Column(db.String,
                          nullable=False,
                          server_default="/static/default_profile.jpg")
    posts = db.relationship('Post')


class Post(db.Model):
    """ Posts in the blog website """

    __tablename__ = "posts"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    title = db.Column(db.String(50),
                      nullable=False)
    content = db.Column(db.Text,
                        nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           nullable=False,
                           server_default=db.func.now())
    user_id = db.Column(db.Integer,
                        db.ForeignKey("users.id"),
                        nullable=False)
    user = db.relationship('User')

    tags = db.relationship('Tag',
                           secondary="posts_tags",
                           bref="posts")


class Tag(db.Model):
    """ Tags that can be placed with
        posts in the blog website """

    __tablename__ = "tags"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    name = db.Column(db.String(15),
                     nullable=False)


class PostTag(db.Model):
    """ A table that keeps track of all the posts and tags """

    __tablename__ = "posts_tags"

    post_id = db.Column(db.Integer,
                        db.ForeignKey('posts.id'),
                        primary_key=True)
    tag_id = db.Column(db.Integer,
                       db.ForeignKey('tags.id'),
                       primary_key=True)
