from igramscraper.instagram import Instagram
from datetime import datetime
import time
import numpy as np
import re 
from .models import User, db

#setting up the environment 
one_week = 604800
instagram = Instagram()

def to_list_str(string):
    #convertion function for storing in the database for strings
    if string!='[]' and string!='None':
        strs = string.replace('[','').replace(']','').replace("'", '').replace('"', '').replace(' ', '').split(',')
        return strs
    else:
        return None
    

def to_list_int(integer):
    #convertion function for the database for integers
    if integer!='[]' and integer!='None':
        ints = integer.replace('[','').replace(']','').split(',')
        lst = [int(i) for i in ints]
        return lst
    else:
        return None

#creating backup account redirections in case the user is blocked by Instagram for too many requests

def backup_account4():
    username = "cs162_content_suggestion4"
    password = "akma123"

    instagram.with_credentials(username, password)
    try:
        instagram.login()
    except:
        instagram.login(two_step_verificator=True)
        
def backup_account3():
    username = "cs162_content_suggestion3"
    password = "akma123"

    instagram.with_credentials(username, password)
    try:
        instagram.login()
    except:
        instagram.login(two_step_verificator=True)
    
def backup_account2():
    username = "cs162_content_suggestion2"
    password = "akma123"
    
    instagram.with_credentials(username, password)
    try:
        instagram.login()
    except:
        instagram.login(two_step_verificator=True)
    
def backup_account1():
    username = "cs162_content_suggestion"
    password = "akma123"

    instagram.with_credentials(username, password)
    try:
        instagram.login()
    except:
        instagram.login(two_step_verificator=True)
#laddered login into instagram to make sure at least one of them succeeds
def instagram_login(username, password):
    try:
        #handle exceptions
        instagram.with_credentials(username, password)
        try:
            instagram.login()
        except:
            instagram.login(two_step_verificator=True)
    except:
        try:
            backup_account4()
        except:
            try:
                backup_account3()
            except:
                try:
                    backup_account2()
                except:
                    try: 
                        backup_account1()
                    except:
                        return 'error'
                
def profile(idx, username, password, target_user):
    '''Function for querying the number of posts and follower count.'''
    # instagram_login(username, password)
    user = User.query.filter_by(id=idx).first()
    try:
        #making sure runs every 5 minutes
        if user.media!=None and time.time()-user.time<300:
            media = user.media
            followers = user.followers
            return user.media, user.followers
            #add time 
        else:
            #adding the data to the database so unnecessary queries are not made
            account = instagram.get_account(target_user)
            user.media = account.media_count
            user.followers = account.followed_by_count
            user.time = time.time()

            db.session.add(user)
            db.session.commit()

            return account.media_count, account.followed_by_count
    except:
        return None, None
# profile("cs162_content_suggestion", "akma123", "cs162_content_suggestion")

def update(medias, username, password, target_user):
    '''Function for querying the comparison between the previous and current weeks. Q
    Queries likes, comments, posts, average likes comparison.'''

    posts_cur = 0
    posts_prev = 0
    likes_cur = []
    likes_prev = []
    comments_cur = 0
    comments_prev = 0

    if medias == None:
        return None, None, None, None
    #going through each post in 50 and making sure for this week we take the most recent (7 days) posts
    #while for the previous week the posts between 2 weeks and 1 week ago
    for media in medias:
        if media.created_time > round(time.time())-one_week:
            posts_cur += 1
            likes_cur.append(media.likes_count)
            comments_cur += media.comments_count
        if (media.created_time < round(time.time())-one_week) & (media.created_time > round(time.time())-2*one_week):
            posts_prev += 1
            likes_prev.append(media.likes_count)
            comments_prev += media.comments_count

    posts_update = posts_cur-posts_prev
    likes_update = np.sum(likes_cur)-np.sum(likes_prev)

    avg_cur = np.mean(likes_cur) if len(likes_cur) != 0 else 0
    avg_prev = np.mean(likes_prev) if len(likes_prev) != 0 else 0

    avg_likes_update = round(avg_cur - avg_prev)
    comments_update = comments_cur-comments_prev

    return posts_update, likes_update, avg_likes_update, comments_update


def user_hashtags(medias, username, password, target_user):
    '''Function for querying the most popular hashtags with the number of times used and overall stats.'''

    hashtags = []
    likes = dict()
    count = dict()
    comments = dict()
    
    if medias == None:
        return None, None, None, None

    #if not enough data, changing the output
    if len(medias)>2:
        for media in medias:
            for tag in media.caption.split():
                if tag.startswith("#"):
                    hashtags.append(re.sub(r"[^A-Za-z0-9_]+", '', tag.strip("#")))

        unique = set(hashtags)

        for hasht in unique:
            likes[hasht] = 0
            comments[hasht] = 0
            count[hasht] = hashtags.count(hasht)

        for media in medias:
            for hasht in unique:
                caption = media.caption.split(" ")
                if ("#"+hasht) in caption:
                    likes[hasht] += media.likes_count
                    comments[hasht] += media.comments_count

        sort = sorted(likes.items(), key=lambda x: x[1], reverse=True)

        hasht = []
        count_res = []
        likes_res = []
        comments_res = []

        for item in sort:
            hasht.append(item[0])
            likes_res.append(item[1])
            comments_res.append(comments[item[0]])
            count_res.append(count[item[0]])
            
        return hasht, count_res, likes_res, comments_res
    else:
        return None, None, None, None


def popular_posts(medias, username, password, target_user):
    '''Function for querying the stats for popular posts by likes.'''
    
    if medias == None:
        return None, None, None, None

    #if not enough data, changing the output
    if len(medias)>2:
        likes_dict = dict()

        for index, media in enumerate(medias):
            likes_dict[index]=media.likes_count
        
        avg_com = round(np.mean([media.comments_count for media in medias]))
        avg_like = round(np.mean([media.likes_count for media in medias]))
        
        sort = sorted(likes_dict.items(), key=lambda x: x[1], reverse=True)[:3]
        
        likes = []
        dates = []
        captions = []
        comments = []
        links = []

        for item in sort:
            media = medias[item[0]]
            likes.append(item[1]-avg_like)
            comments.append(media.comments_count-avg_com)
            dates.append(datetime.fromtimestamp(media.created_time).strftime("%B %d, %Y"))
            captions.append(media.caption[:100])
            links.append(media.link)

        return likes, dates, captions, comments, links
    else:
        return None, None, None, None, None 

