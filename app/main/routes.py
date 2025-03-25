import os
from datetime import datetime, timezone
from urllib import request

from flask_login import current_user
from app import db
from app.main import bp
from flask import render_template, flash, redirect, url_for, request, current_app
from app.main.forms import PostForm
from app.models import Post


# user = {'username': 'Miguel'}
# posts = [
#     {
#         'author': {'username': 'John'},
#         'body': 'Beautiful day in Portland!'
#     },
#     {
#         'author': {'username': 'Susan'},
#         'body': 'The Avengers movie was so cool!'
#     }
# ]
@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    form = PostForm()

    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()

        flash('Your post is now posted.')
        redirect(url_for('main.index'))

    page = request.args.get('page', 1, type=int)
    posts = db.paginate(current_user.following_posts(), page=page, per_page=current_app.config['POSTS_PER_PAGE'],
                        error_out=False)
    return render_template('index.html', title='Home', user=user, posts=posts)


@bp.route('/user/<username>')
def user(username):
    render_template()
