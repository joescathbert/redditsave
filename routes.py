from run import app
from flask import render_template, request, url_for, redirect
from dotenv import load_dotenv
import os
from models.redditposts import RedditModel
from models.redditsaved import RedditSavedModel

REDDIT_OBJECT = None
REDDIT_SAVED_OBJECT = RedditSavedModel()

CURRENT_FOLDER = 0

load_dotenv()

def get_folder_item_list(current_folder):
    saved_folders_list = REDDIT_SAVED_OBJECT.get_saved_folders(parent_folder_id=current_folder)
    return [{'id': saved_folder['folder_id'], 'name': saved_folder['folder_name'], 'type': 'folder'} for saved_folder in saved_folders_list]

def do_up_folder(current_folder):
    folder = REDDIT_SAVED_OBJECT.get_folder(folder_id=current_folder)
    return folder['parent_folder_id']



@app.route('/', methods=['GET', 'POST'])
def home():
    global REDDIT_OBJECT, CURRENT_FOLDER
    if request.method == 'POST':
        item_type = request.form['itemtype']
        print(item_type)

        if item_type == 'folder':
            CURRENT_FOLDER = request.form['itemid']
        if item_type == 'action'  and CURRENT_FOLDER != 0:
            item_id = request.form['itemid']
            if item_id == 'nf':
                return redirect(url_for('new_folder'))
            if item_id == 'uf':
                    CURRENT_FOLDER = do_up_folder(current_folder=CURRENT_FOLDER)
                
        # post_object = REDDIT_OBJECT.get_post_object(post_id=post_id)
        # print(REDDIT_OBJECT.get_media_url(post=post_object))

    if not REDDIT_OBJECT:
        REDDIT_OBJECT = RedditModel(client_id=os.environ['reddit_client_id'], client_secret=os.environ['reddit_client_secret'], 
            user_agent=os.environ['reddit_user_agent'], username=os.environ['reddit_username'], password=os.environ['reddit_password'])

    # post_list = [{'title': post.title, 'id': post.id} for post in REDDIT_OBJECT.get_saved_posts(username=os.environ['reddit_username'], limit=20)]

    print(CURRENT_FOLDER)
    item_list = get_folder_item_list(current_folder=CURRENT_FOLDER)
    print(item_list)
    return render_template('home.html', item_list=item_list)

@app.route('/new_folder', methods=['GET', 'POST'])
def new_folder():
    if CURRENT_FOLDER == 0:
        return redirect(url_for('home'))

    if request.method == 'POST':
        folder_name = request.form['foldername']
        print(folder_name)
        REDDIT_SAVED_OBJECT.create_saved_folder(folder_name=folder_name, parent_folder_id=CURRENT_FOLDER, reddit_username=os.environ['reddit_username'])
        return redirect(url_for('home'))
    
    return render_template('newfolder.html')
