import requests
import json

class RedditSavedModel:
    def __init__(self):
        self.api_url = 'http://127.0.0.1:5000/redditsaveapi'

    def add_user(self, reddit_username):
        user_details = self.get_user(reddit_username=reddit_username)
        if not user_details:
            response = requests.get(url=f'{self.api_url}/add_user/{reddit_username}')
            data = json.loads(response.text)
            print(data)
            return data
        return user_details

    def get_user(self, reddit_username):
        response = requests.get(url=f'{self.api_url}/get_user/{reddit_username}')
        data = json.loads(response.text)
        print(data)
        return data

    def create_saved_folder(self, folder_name, parent_folder_id, reddit_username):
        response = requests.get(url=f'{self.api_url}/create_saved_folder/{folder_name}/{parent_folder_id}/{reddit_username}')
        data = json.loads(response.text)
        print(data)

    def get_saved_folders(self, parent_folder_id):
        response = requests.get(url=f'{self.api_url}/get_saved_folders/{parent_folder_id}')
        data = json.loads(response.text)
        return data

    def add_post(self, post_name, post_id, parent_folder_id, reddit_username):
        response = requests.get(url=f'{self.api_url}/add_post/{post_name}/{post_id}/{parent_folder_id}/{reddit_username}/')
        data = json.loads(response.text)
        print(data)
        
    def get_saved_posts(self, parent_folder_id):
        response = requests.get(url=f'{self.api_url}/get_saved_posts/{parent_folder_id}')
        data = json.loads(response.text)
        return data

    def get_item(self, item_id):
        response = requests.get(url=f'{self.api_url}/get_item/{item_id}')
        data = json.loads(response.text)
        return data