# ==================================    ADMIN VIEWS    ==========================================
# Code adapted from:
# https://github.com/flask-admin/flask-admin/tree/master/examples/auth-flask-login 
# Many thanks.

from flask import request, redirect, url_for, abort, flash
from flask_login import current_user, login_user, logout_user

import flask_admin as admin
from flask_admin.contrib import sqla
from flask_admin import helpers, expose
from flask_admin.contrib.sqla import ModelView

from cinescout import db # Get db object defined in __init__.py
from cinescout.models import User
from cinescout.admin.forms import AdminLoginForm, AdminAddUserForm, AdminResetPasswordForm


# Create customized model view class.
class CinescoutModelView(ModelView):
    """Handles admin panel display of database models and what actions can be taken on them."""

    def is_accessible(self):
        """Defines who can access the admin panel."""
        return current_user.is_authenticated and current_user.username == 'admin'


# Create customized index view class that handles login & registration.
class MyAdminIndexView(admin.AdminIndexView):
    """Creates views for admin panel part of website."""

    @expose('/')
    def index(self):
        """Point of entry. Any unauthenticated user that is not admin is redirected to login.
        Otherwise, allow access to database views.
        """
        if not current_user.is_authenticated or current_user.username != 'admin':
            return redirect(url_for('.login_view'))

        # admin logged in. Make database models available in admin panel.
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        """Processes posted login form data. Otherwise returns login form fields for
        non-logged in users."""
        form = AdminLoginForm()

        # Assuming form data has been POSTED...
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()

            print(user)

            if (user is None 
                or user.username != 'admin' 
                or user.password_hash is None
                or form.password.data is None 
                or form.password.data.strip() == ""
                or not user.check_password(form.password.data)):

                flash('Invalid username or password.', 'error')
                return redirect(url_for('.login_view'))
            
            # admin gets access.
            login_user(user)
        
        # admin already logged in. Make database tables available...
        if current_user.is_authenticated and current_user.username == 'admin':
            return redirect(url_for('.index'))

        # GET request made by non-logged in user. Return login form so it can be displayed.
        self._template_args['form'] = form

        return super(MyAdminIndexView, self).index()

    @expose('/add-user', methods=('GET', 'POST'))
    def add_user(self):
        """Adds new Cinescout user."""

        # Only web admin can add users. Forbid access otherwise.
        if not current_user.is_authenticated or current_user.username != 'admin':
            abort(403)
        
        form = AdminAddUserForm()

         # Assuming form data has been POSTED, check various fields for proper input. 
        if form.validate_on_submit():
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash(f'User "{form.username.data}" added to database.', 'success')
            return redirect(url_for('.add_user'))

        # Render add-user form (GET request)   
        # Args to be used in /admin/index.html
        self._template_args['adduser'] = True
        self._template_args['title'] = "Add User"
        self._template_args['form'] = form

        return super(MyAdminIndexView, self).index()

    @expose('/reset-password', methods=('GET', 'POST'))
    def reset_password(self):
        """Allows site administator to reset user password in case forgotten, e.g."""

        # Forbid access.
        if not current_user.is_authenticated or current_user.username != 'admin':
            abort(403)
            
        form = AdminResetPasswordForm()

         # Assuming form data has been POSTED, check various fields for proper input. 
        if form.validate_on_submit():

            # Get data.
            username = form.username.data.strip()
            new_password = form.password.data

            # See whether specified user in db. 
            user = User.query.filter_by(username=username).first()
            if user == None:
                flash("Reset password failed: username not in database.", "error")
                return redirect(url_for('.reset_password'))

            # Reset users password to something new.
            user.set_password(password=new_password)
            db.session.commit()

            flash(f'Password for user "{username}" updated!', 'success')
            return redirect(url_for('.reset_password'))

        # Render add-user form (GET request)   
        # Args to be used in /admin/index.html
        self._template_args['resetpw'] = True
        self._template_args['title'] = "Reset Password"
        self._template_args['form'] = form

        return super(MyAdminIndexView, self).index()
        
    @expose('/logout/')
    def logout_view(self):
        logout_user()
        return redirect(url_for('.index'))