from flask import Flask, render_template, request, flash, request, redirect, url_for, Blueprint, Response
from .models import User, Category, db, bcrypt
import json
import jwt
import os
import re 
import time 
from .getdata import getTrends, create_figure
from sqlalchemy import and_, or_, not_
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime
from .mail import mail
from flask_login import LoginManager
from .forms import UpdateUsernameForm, UpdateEmailForm, SupportForm, UpdatePreferences
from flask_mail import Message
from cryptography.fernet import Fernet
from .insights import update, user_hashtags, popular_posts, profile, instagram_login, instagram, to_list_str, to_list_int
from .suggestions import get_media_hashtag

# new application blueprint for routes
routes = Blueprint('routes', __name__, template_folder='templates')

def decrypt_instagram_password():
    # Decrypting instagram password.
    if current_user and current_user.is_authenticated:
        f = Fernet(user.instagram_key.encode('ascii'))
        password = f.decrypt(user.instagram_password.encode('ascii'))
        return password
    return None

# app routes
@routes.route("/about")
def about():
    return render_template('home.html')


@routes.route("/", methods=['POST', 'GET'])
def dashboard():
    if current_user and current_user.is_authenticated:
        return redirect(url_for('routes.suggestions'))
    return render_template('home.html')


@routes.route("/insights", methods=['POST', 'GET'])
def insights():
    if current_user and current_user.is_authenticated:
        # scraping Instagram for the data for the insights page 
        user = User.query.filter_by(id=current_user.id).first()

        output = instagram_login(current_user.instagram_username, current_user.instagram_password)
        
        #handling all of the errors so it doesn't stop working
        if output=='error':
            posts, followers = None, None
            posts_update, likes_update, avg_likes_update, comments_update = None, None, None, None 
            hasht, count_res, likes_res, comments_res = None, None, None, None 
            likes, dates, captions, comments, links = None, None, None, None, None
        else:
            posts, followers = profile(current_user.id, current_user.instagram_username, current_user.instagram_password, current_user.instagram_username)
            
            #making sure it runs every 5 minutes
            if user.posts_update!=None and time.time()-user.time<300:
                posts_update, likes_update, avg_likes_update, comments_update = user.posts_update, user.likes_update, user.avg_likes_update, user.comments_update
                hasht, count_res, likes_res, comments_res = to_list_str(user.hasht), to_list_int(user.count_res), to_list_int(user.likes_res), to_list_int(user.comments_res)
                likes, dates, captions, comments, links = to_list_int(user.likes), to_list_str(user.dates), to_list_str(user.captions), to_list_int(user.comments), to_list_str(user.links)
            else:
                try:
                    #getting the data once for all
                    medias = instagram.get_medias(current_user.instagram_username, 30)
                    posts_update, likes_update, avg_likes_update, comments_update = update(medias, 
                        current_user.instagram_username, current_user.instagram_password, current_user.instagram_username)
                    hasht, count_res, likes_res, comments_res = user_hashtags(medias, 
                        current_user.instagram_username, current_user.instagram_password, current_user.instagram_username)
                    likes, dates, captions, comments, links = popular_posts(medias, current_user.instagram_username, current_user.instagram_password, current_user.instagram_username)
                    
                    user.posts_update, user.likes_update, user.avg_likes_update, user.comments_update = posts_update, likes_update, avg_likes_update, comments_update
                    user.hasht, user.count_res, user.likes_res, user.comments_res = str(hasht), str(count_res), str(likes_res), str(comments_res)
                    user.likes, user.dates, user.captions, user.comments, user.links = str(likes), str(dates), str(captions), str(comments), str(links)
                    user.now = time.time()
                    
                    db.session.add(user)
                    db.session.commit()
                
                except:
                    medias = None

                    posts_update, likes_update, avg_likes_update, comments_update = None, None, None, None 
                    hasht, count_res, likes_res, comments_res = None, None, None, None 
                    likes, dates, captions, comments, links = None, None, None, None, None
                    
        return render_template('insights.html', posts_update=posts_update, likes_update=likes_update, avg_likes_update=avg_likes_update, comments_update=comments_update, hasht=hasht, count_res=count_res, likes_res=likes_res, comments_res=comments_res, likes=likes, dates=dates, captions=captions, comments=comments, links=links, posts=posts, followers=followers)
    return render_template('home.html')

@routes.route("/suggestions", methods=['POST', 'GET'])
def suggestions():
    form_update_preferences = UpdatePreferences(request.form)
    if current_user and current_user.is_authenticated:
        categories = [cat for cat in Category.query.filter_by(user_id=current_user.id)]
        #mock data for now
        hashtag = ["jujutsukaisen", "haikyuu", "bnha"]
        examples = get_media_hashtag(current_user.instagram_username, current_user.instagram_password, hashtag)
        return render_template(
                'suggestions.html', 
                form_update_preferences=form_update_preferences,
                categories=categories, examples=examples)
    return render_template('home.html')

@routes.route("/update_preferences", methods=['POST'])
def update_preferences():
    #function for updating the preferences
    form_update_preferences = UpdatePreferences(request.form)

    if current_user and current_user.is_authenticated:

        if form_update_preferences.validate_on_submit():
            # updating email if form validates
            user = User.query.filter_by(id=current_user.id).first()
            user.analyze_posts = form_update_preferences.analyze.data
            
            db.session.add(user)
            
            #deleting the previous history and writing over
            cats = Category.query.filter_by(user_id=current_user.id)
            for cat in cats:
                db.session.delete(cat)

            hashtags = []
            for tag in form_update_preferences.categories.data.split():
                if tag.startswith("#"):
                    hashtags.append(re.sub(r"[^A-Za-z0-9_]+", '', tag.strip("#")))

            #adding the new hashtags
            for cat in set(hashtags):
                new_category = Category(user_id=current_user.id, keyword=cat)
                db.session.add(new_category)

            #committing the changes
            db.session.commit()
            flash(f'Preferences saved!', 'success')
            return redirect(url_for('routes.suggestions'))
        else:
            #rendering the template and showing the current categories
            categories = [cat for cat in Category.query.filter_by(user_id=current_user.id)]
            return render_template(
                'suggestions.html', 
                form_update_preferences=form_update_preferences,
                categories=categories, examples=None)
        return redirect(url_for('routes.suggestions'))
    # return user home if not logged in
    return redirect(url_for('routes.home'))

@routes.route("/support", methods=['POST', 'GET'])
def support():
    form = SupportForm(request.form)

    if request.method == 'GET':
        if current_user and current_user.is_authenticated:
            return render_template('support.html', form=form)
        return render_template('home.html')
    elif request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(id=current_user.id).first()
            msg = Message(
            subject=form.topic.data, 
            sender=user.email, 
            recipients=[os.getenv('MAIL_USERNAME')]
            )
            msg.html = render_template("email_templates/support_email.html", username=user.username, description=form.description.data)
            mail.send(msg)
            flash('Thanks for entering in contact with our Support, we will reply soon!', 'success')
            return redirect(url_for('routes.support'))
        else:
            print("Support form errors:", form.errors.items())
            return render_template('support.html', form=form)


@routes.route('/users')
def users():
    users = User.query.all()
    return render_template('users.html', users=users)


@routes.route("/trend_over_time", methods=['GET', 'POST'])
def show_trends():
    if request.method == 'POST':
        kw = request.form['trend_for']
        create_figure(kw)
        return render_template("trends.html", trends=kw)
