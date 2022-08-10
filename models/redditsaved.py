import requests
import json

class RedditSavedModel:
    def __init__(self):
        self.api_url = 'http://127.0.0.1:5000/redditsaveapi/'

    def get_saved_folders(self, parent_folder_id):
        response = requests.get(url=f'{self.api_url}/get_saved_folders/{parent_folder_id}')
        data = json.loads(response.text)
        print(data)
        data = [dict(x,  type='folder') for x in data]
        return data

    def get_folder(self, folder_id):
        response = requests.get(url=f'{self.api_url}/get_folder/{folder_id}')
        data = json.loads(response.text)
        return data

    def create_saved_folder(self, folder_name, parent_folder_id, reddit_username):
        response = requests.get(url=f'{self.api_url}/create_saved_folder/{folder_name}/{parent_folder_id}/{reddit_username}')
        data = json.loads(response.text)
        print(data)

    