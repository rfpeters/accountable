# accountable politics
# app.py

import os
from flask import (Flask, g, render_template, flash, redirect, url_for, abort)
from flask.ext.bcrypt import check_password_hash
from flask.ext.login import (LoginManager, login_user, logout_user,
                             login_required, current_user)
import forms
import models


DEBUG = True
PORT = 5000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 's_e_c_r_e_t___k_e_y!'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Specify the current user and connect to the database before each request."""
    g.user = current_user
    g.db = models.db_proxy
    g.db.connect()


@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response


@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("You successfully signed up!", "success")
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email or password doesn't match!", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You are logged in!", "success")
                return redirect(url_for('index'))
            else:
                flash("Your email or password doesn't match!", "error")
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out!", "success")
    return redirect(url_for('index'))


@app.route('/new_post', methods=('GET', 'POST'))
@login_required
def post():
    form = forms.PostForm()
    if form.validate_on_submit():
        models.Post.create(user=g.user.id,
                           content=form.content.data.strip())
        flash("Message posted!", "success")
        return redirect(url_for('index'))
    return render_template('post.html', form=form)


@app.route('/')
def index():
    stream = models.Post.select().limit(100)
    return render_template('stream.html', stream=stream)


@app.route('/stream')
@app.route('/stream/<username>')
def stream(username=None):
    template = 'stream.html'
    if username and username != current_user.username:
        try:
            user = models.User.select().where(
                models.User.username**username).get()
        except models.DoesNotExist:
            abort(404) # if user does not exist send error
        else:
            stream = user.posts.limit(100)
    else:
        stream = current_user.get_stream().limit(100)
        user = current_user
    if username:
        template = 'user_stream.html'
    return render_template(template, stream=stream, user=user)


@app.route('/post/<int:post_id>')
def view_post(post_id):
    """Get all the posts that have this id"""
    posts = models.Post.select().where(models.Post.id == post_id)
    if posts.count() == 0:
        abort(404)
    return render_template('stream.html', stream=posts)


@app.route('/delete_post/<int:post_id>')
@login_required
def delete_post(post_id):
    post = models.Post.delete().where(models.Post.id == post_id).execute()
    flash("This post has successfully been deleted.", "success")
    return redirect(url_for('stream', stream=stream))


@app.route('/follow/<username>')
@login_required
def follow(username):
    try:
        to_user = models.User.get(models.User.username**username)
    except models.DoesNotExist:
        abort(404)
    else:
        try:
            models.Relationship.create(
                from_user=g.user._get_current_object(),
                to_user=to_user
            )
        except models.IntegrityError:
            pass
        else:
            flash("You're now following {}!".format(to_user.username), "success")
    return redirect(url_for('stream', username=to_user.username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    try:
        to_user = models.User.get(models.User.username**username)
    except models.DoesNotExist:
        abort(404)
    else:
        try:
            models.Relationship.get(
                from_user=g.user._get_current_object(),
                to_user=to_user
            ).delete_instance()
        except models.IntegrityError:
            pass
            flash("You are no longer following {}!".format(to_user.username), "success")
    return redirect(url_for('stream', username=to_user.username))


@app.route('/upvote/<int:post_id>')
@login_required
def upvote(post_id):
    post = models.Post.select().where(models.Post.id == post_id)
    models.Upvote.create(user=g.user.id, post=post_id)
    flash("Vote Registered!", "success")
    return redirect(url_for('index'))


@app.route('/downvote/<int:post_id>')
@login_required
def downvote(post_id):
    post = models.Post.select().where(models.Post.id == post_id)
    models.Downvote.create(user=g.user.id, post=post_id)
    flash("Vote Registered!", "success")
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    models.initialize()
    try:
        models.User.create_user(
            username='matt',
            email='matt@example.com',
            password='password',
            admin=True
        )
    except ValueError:
        pass
    app.run(debug=DEBUG, host=HOST, port=PORT)