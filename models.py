# accountable politics
# models.py

import datetime
import os
from flask.ext.bcrypt import generate_password_hash
from flask.ext.login import UserMixin
from peewee import *
import urllib
from urllib.parse import urlparse
import psycopg2

db_proxy = Proxy()

# heroku config:set HEROKU=1
if 'HEROKU' in os.environ:
    urllib.parse.uses_netloc.append('postgres')
    url = urlparse(os.environ["DATABASE_URL"])
    db = PostgresqlDatabase(database=url.path[1:], user=url.username, password=url.password, host=url.hostname, port=url.port)
    db_proxy.initialize(db)
else:
    db = SqliteDatabase('accountable.db')
    db_proxy.initialize(db)


class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now())
    is_admin = BooleanField(default=False)

    class Meta:
        database = db_proxy
        order_by = ('-joined_at',)

    def get_posts(self):
        return Post.select().where(Post.user == self)

    def get_stream(self):
        return Post.select().where(
            (Post.user << self.following()) | # get the posts where the post author is inside of the people I follow
            (Post.user == self) # get all of the current users authored posts
        )

    def following(self):
        """The users that current user following"""
        return (
            User.select().join(
                Relationship, on=Relationship.to_user
            ).where(
                Relationship.from_user == self
            )
        )

    def followers(self):
        """Get users following the current user"""
        return (
            User.select().join(
                Relationship, on=Relationship.from_user
            ).where(
                Relationship.to_user == self
            )
        )

    @classmethod
    def create_user(cls, username, email, password, admin=False):
        try:
            with db_proxy.transaction():
                cls.create(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    is_admin=admin)
        except IntegrityError:
            raise ValueError("User already exists")


class Post(Model):
    timestamp = DateTimeField(default=datetime.datetime.now())
    user = ForeignKeyField(
        rel_model=User,
        related_name='posts'
    )
    content = TextField()

    class Meta:
        database = db_proxy
        order_by = ('-timestamp',)


class Upvote(Model):
    post = ForeignKeyField(
        rel_model=Post,
        related_name='upvotes'
    )
    user = ForeignKeyField(
        rel_model=User,
        related_name='upvotes'
    )

    class Meta:
        database = db_proxy


class Downvote(Model):
    post = ForeignKeyField(
        rel_model=Post,
        related_name='downvotes'
    )
    user = ForeignKeyField(
        rel_model=User,
        related_name='downvotes'
    )

    class Meta:
        database = db_proxy


class Relationship(Model):
    from_user = ForeignKeyField(User, related_name='relationships')
    to_user = ForeignKeyField(User, related_name='related_to')

    class Meta:
        database = db_proxy
        indexes = (
            (('from_user', 'to_user'), True),  # trailing comma required
        )


def initialize():
    db_proxy.connect()
    db_proxy.create_tables([User, Post, Relationship, Upvote, Downvote], safe=True)

