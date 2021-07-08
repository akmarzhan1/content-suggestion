from igramscraper.instagram import Instagram
from datetime import datetime
import time
import numpy as np
from .insights import instagram_login

instagram = Instagram()

#not working for now due to libtary issues

# def get_media_hashtag(username, password, hashtag):

#     instagram_login(username, password)

#     if len(hashtag)==3:
#         for hasht in hashtag:
#             medias = instagram.get_medias_by_tag('instagood', count=2)
#             info = [] #owner, likes, comments, 

#             medium = []
#             medium.append(medias[0].owner)
#             medium.append(medias[0].likes_count)
#             medium.append(medias[0].comments_count)
#             medium.append(medias[0].caption[:100]+"...")
#             medium.append(medias[0].link)
#             medium.append(medias[0].image_thumbnail_url)
#             info.append(medium)
#             # for media in medias[0]:
#             #     medium = []
#             #     medium.append(media.owner)
#             #     medium.append(media.likes_count)
#             #     medium.append(media.comments_count)
#             #     medium.append(media.caption[:100]+"...")
#             #     medium.append(media.link)
#             #     mediumm.append(media.image_thumbnail_url)
#             #     info.append(medium)
#         return info
#     else:
#         return None

#mock data
def get_media_hashtag(username, password, hashtag):
    hola = ['kylie123', 123900, 338, "Hello beautiful people:)", "https://www.instagram.com/p/CNXxbREolCR/", "https://mrreiha.keybase.pub/codepen/hover-fx/news2.png"]
    return [hola, hola, hola]
