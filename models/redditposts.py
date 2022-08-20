import praw
import requests
from urllib.parse import unquote


class RedditModel:
    def __init__(self, client_id, client_secret, user_agent):
        self.reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, redirect_uri="http://192.168.0.112:5000", user_agent=user_agent)
    
    def get_auth_url(self):
        return self.reddit.auth.url(scopes=["identity", "history", "read"], state="hi", duration="permanent")

    def authorize_app(self, code):
        print(self.reddit.auth.authorize(code))

    def get_reddit_username(self):
        return self.reddit.user.me().name

    def get_post_object(self, post_id):
        return self.reddit.submission(id=post_id)

    def get_search_posts(self, subreddit_name, query, sort="relevance", limit=10, time_filter='all'):
        return [post for post in self.reddit.subreddit(subreddit_name).search(query=query, sort=sort, time_filter=time_filter, limit=limit)]

    def get_saved_posts(self, username, limit):
        return [post for post in self.reddit.redditor(username).saved(limit=limit) if isinstance(post, praw.models.reddit.submission.Submission) and self.get_media_url(post=post)[0]]
        
    @staticmethod
    def down_media(media_url, media_file_name):
        if media_url and media_file_name:
            response = requests.get(media_url)
            media_file_name = media_file_name.translate({ord(c):None for c in "<>:\"/\\|?*"})
            with open(f'media\\{media_file_name}', "wb") as media_file:
                media_file.write(response.content)

    @staticmethod
    def get_media_content(media_url, media_file_name):
        if media_url and media_file_name:
            response = requests.get(media_url)
            return response.content

    @staticmethod
    def get_media_url(post):
        media_url, media_file_name = '', ''
        if post.is_video:
            media_url = post.media['reddit_video']['fallback_url']
            media_file_name = f'{post.title} - {media_url.split("/")[4].split("?")[0]}'     
        elif post.media and post.media['type'] in ['gfycat.com', 'redgifs.com']:
            thumbnail_url = post.media['oembed']['thumbnail_url']
            if thumbnail_url.split("/")[2] not in ['thumbs.gfycat.com', 'thumbs2.redgifs.com']:
                thumbnail_url = thumbnail_url.split("&")[0].split("=")[1]
                thumbnail_url = unquote(thumbnail_url)
            media_url = thumbnail_url.replace("size_restricted.gif", "mobile.mp4" )
            media_url = media_url.replace("mobile.jpg", "mobile.mp4")
            media_file_name = f'{post.title} - {media_url.split("/")[3]}'
        return media_url, media_file_name
        
    def download_media(self, post):
        self.down_media(*self.get_media_url(post))