
from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required

from cinescout import app
from cinescout.models import User
from cinescout.auth.forms import LoginForm

# Import Blueprint object.
from cinescout.auth import bp

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Log-in user with valid credentials. Reject otherwise."""

    # Logged-in users don't get to log-in before logging out again.
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password.', 'error')
            return redirect(url_for('auth.login'))

        # Remember user id in case session ended and user then re-enters app,
        # e.g. closing tab while still logged-in.
        login_user(user, remember=form.remember_me.data)
        flash('You have been logged in!', 'success')
        return redirect(url_for('main.search'))

    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
@login_required
def logout():
    """Logs out user."""
    logout_user()
    flash('You have been logged out!', 'success')
    return redirect(url_for('auth.login'))


# For disabled Registration feature
# from cinescout import db 
# from cinescout.forms import RegistrationForm

# Disabled as of version 1.1.0
# UPDATE FOR BLUEPRINT USE!
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     """Allows non-logged in users to register for account."""

#     # Logged in users shouldn't be allowed to register.
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))

#     form = RegistrationForm()

#     # Ensure user-entered data is good. If so, register and take to login page!
#     if form.validate_on_submit():
#         user = User(username=form.username.data, email=form.email.data)
#         user.set_password(form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         flash(f'Welcome to Cinescout, {form.username.data}! Now login to get started.', 'success')
#         return redirect(url_for('login'))

#     # When users GET the register page
#     return render_template('register.html', title='Register', form=form)