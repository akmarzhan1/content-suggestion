import random
import string
from flask import Flask, render_template, request, redirect, url_for, Blueprint, flash
from .models import User, db, bcrypt
from .mail import mail
import json, jwt, os
from datetime import datetime, timedelta
from flask_mail import Message
from flask_login import login_user, current_user, logout_user, login_required, LoginManager
from .forms import RegistrationForm, LoginForm, ResetForm, ResetPasswordForm
from cryptography.fernet import Fernet

# new application blueprint for auth related tasks
auth = Blueprint('auth', __name__, template_folder='templates')

login_manager = LoginManager()

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# registering users
@auth.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'GET':
        if current_user and current_user.is_authenticated:
            return redirect(url_for('routes.dashboard'))
        return render_template('register.html', form=form)
    elif request.method == 'POST':
        # form validation
        if form.validate_on_submit():
            # generating the hashed password and storing it as so
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            # encrypting instagram password
            key = Fernet.generate_key()
            f = Fernet(key)
            # converting bytes key to str to save on DB
            key = key.decode('ascii')
            encrypted_insta_password = f.encrypt(form.instagram_password.data.encode('ascii')).decode('ascii')
            user = User(
                username=form.username.data, 
                email=form.email.data, 
                password=hashed_password, 
                instagram_username=form.instagram_username.data,
                instagram_password=encrypted_insta_password,
                instagram_key=key
            )
            db.session.add(user)
            db.session.commit()
            flash(f'Congrats on successful account creation, {form.username.data}!', 'success')
            return redirect(url_for('auth.login'))
        else:
            print("Register form errors:", form.errors.items())
            return render_template('register.html', title="Register", form=form)

def check_password(user_password, password):
    # check if passsord provided by user is the correct one
    return bcrypt.check_password_hash(user_password, password)

# logging users in
@auth.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'GET':
        if current_user and current_user.is_authenticated:
            return redirect(url_for('routes.suggestions'))
        return render_template('login.html', title="Login", form=form)
    else:
        if not form.validate_on_submit():
            print("Login form errors:", form.errors.items())
            return render_template('login.html', form=form)
        
        # Login and validate the user.
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not check_password(user.password, form.password.data):
            flash(f'Please try logging in again!', 'danger')
            return redirect(url_for('auth.login'))
        login_user(user)
        # If the user was in a page before logging in
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('routes.suggestions'))

# logging users out
@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route("/reset", methods=['GET', 'POST'])
def reset():
    # user requested password reset route
    form = ResetForm(request.form)
    if request.method == 'GET':
        if current_user and current_user.is_authenticated:
            return redirect(url_for('routes.dashboard'))
        return render_template('reset.html', form=form)
    else:
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            # showing user that email was sent, so no one can use this page to do user enumeration
            flash(f'Email with instructions to reset your password was sent!', 'info')
            return redirect(url_for('auth.login'))
        # current date and time
        now = str(datetime.now())
        encoded_jwt = jwt.encode({"email": form.email.data, "datetime": now}, os.getenv('SECRET_KEY'), algorithm="HS256")

        # saving reset token on DB
        user.reset_token = encoded_jwt
        db.session.commit()
        msg = Message(
            subject="Password Reset Request", 
            sender="no-reply@suggestme.com", 
            recipients=[form.email.data]
        )
        msg.html = render_template("email_templates/reset_password_email.html", username=user.username, link=request.base_url+"/token/"+encoded_jwt.decode("utf-8"))
        mail.send(msg)
        flash(f'Email with instructions to reset your password was sent!', 'info')
        return redirect(url_for('auth.login'))

@auth.route('/reset/token/<encoded_jwt>', methods=['GET', 'POST'])
def reset_token(encoded_jwt):
    # user sent new password after requesting password reset
    form = ResetPasswordForm(request.form)
    if request.method == 'GET':
        # you can only access this page if you're logged out
        if current_user and current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        return render_template('new_password.html', form=form)
    try:
        # get token data
        user_data = jwt.decode(encoded_jwt, os.getenv('SECRET_KEY'), algorithms=["HS256"])
        user_email = user_data['email']
        user_datetime = user_data['datetime']
        # convert str to datetime
        user_datetime = datetime.strptime(user_datetime, '%Y-%m-%d %H:%M:%S.%f')

        # getting user DB data to check if the token is the same
        user = User.query.filter_by(email=user_email).first()
        # if it's not the same from the DB, the time expired, or we didn't found a user: we have an invalid token
        if user is None or user.reset_token != encoded_jwt or not user_datetime + timedelta(hours=1) > datetime.now():
            flash('Invalid token')
            return redirect(url_for('auth.login'))
    except Exception as e:
        print(e)
        # if there is any exception we return an invalid token as well.
        # if we return the same thing for different errors, attackers won't know why they are getting an error.
        flash('Invalid token')
        return redirect(url_for('auth.login'))
    
    if form.validate_on_submit():
        # updating password and cleaning DB token
        hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
        user.password = hashed_password
        user.reset_token = ""
        db.session.commit()
        flash('Password updated!')
        return redirect(url_for('auth.login'))
    print("Form errors:", form.errors.items())
    return render_template('new_password.html', form=form)
