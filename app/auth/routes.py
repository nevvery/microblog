from flask import render_template, redirect, url_for, flash
from app.auth import bp
from app.auth.forms import LoginForm
from app.models import User
from app import db
import sqlalchemy as sa
from flask_login import login_user


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('main.index'))

    return render_template('auth/login.html', title='Login', form=form)
