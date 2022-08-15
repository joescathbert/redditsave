from run import app
from flask import render_template, request, url_for, redirect
from dotenv import load_dotenv
import os
from models.redditposts import RedditModel
from models.redditsaved import RedditSavedModel

load_dotenv()

REDDIT_OBJECT = None
REDDIT_SAVED_OBJECT = RedditSavedModel()
LIMIT = 500

CURRENT_FOLDER = 0

def get_folder_item_list(current_folder):
    saved_folders_list = REDDIT_SAVED_OBJECT.get_saved_folders(parent_folder_id=current_folder)
    return [{'id': saved_folder['folder_id'], 'name': saved_folder['folder_name'], 'type': saved_folder['folder_type']} for saved_folder in saved_folders_list]

def do_up_folder(current_folder):
    folder = REDDIT_SAVED_OBJECT.get_folder(folder_id=current_folder)
    return folder['parent_folder_id']

def get_folder_type(current_folder):
    folder = REDDIT_SAVED_OBJECT.get_folder(folder_id=current_folder)
    return folder['folder_type']

def get_root_folder_id(reddit_username):
    user = REDDIT_SAVED_OBJECT.get_user(reddit_username=reddit_username)
    return user['root_folder_id']

@app.route('/login', methods=['GET', 'POST'])
def login():
    global REDDIT_OBJECT
    if request.method == 'POST':
        if request.form['login'] == 'login':
            REDDIT_OBJECT = RedditModel(client_id=os.environ['reddit_client_id'], client_secret=os.environ['reddit_client_secret'], 
                            user_agent=os.environ['reddit_user_agent'])
            auth_url = REDDIT_OBJECT.get_auth_url()
            return redirect(auth_url)

    return render_template('login.html')


@app.route('/', methods=['GET', 'POST'])
def home():
    global REDDIT_OBJECT, CURRENT_FOLDER, REDDIT_SAVED_OBJECT
    if not REDDIT_OBJECT:
        return redirect(url_for('login'))

    if request.method == 'GET':
        state = request.args.get('state')
        code = request.args.get('code')
        if code:
            REDDIT_OBJECT.authorize_app(code=code)
            REDDIT_SAVED_OBJECT.add_user(reddit_username=REDDIT_OBJECT.get_reddit_username())
            CURRENT_FOLDER = get_root_folder_id(reddit_username=REDDIT_OBJECT.get_reddit_username())   

    item_list = []

    if request.method == 'POST':
        item_type = request.form['itemtype']
        item_id = request.form['itemid']
        print(item_id, item_type)

        if item_type in ['inbuilt_folder', 'user_folder'] :
            CURRENT_FOLDER = int(request.form['itemid'])
            if item_type == 'inbuilt_folder':
                item_list = [{'name': post.title, 'id': post.id, 'type': 'post'} for post in REDDIT_OBJECT.get_saved_posts(username=REDDIT_OBJECT.get_reddit_username(), limit=LIMIT)]

        if item_type == 'action' and CURRENT_FOLDER != get_root_folder_id(reddit_username=REDDIT_OBJECT.get_reddit_username()):
            if item_id == 'nf' and get_folder_type(current_folder=CURRENT_FOLDER) == 'user_folder':
                return redirect(url_for('new_folder'))
            if item_id == 'uf':
                CURRENT_FOLDER = do_up_folder(current_folder=CURRENT_FOLDER)

        if item_type == 'post':
            return redirect(url_for('playback', post_id=item_id))

    print(CURRENT_FOLDER)
    if CURRENT_FOLDER == get_root_folder_id(reddit_username=REDDIT_OBJECT.get_reddit_username()) + 1:
        item_list = [{'name': post.title, 'id': post.id, 'type': 'post'} for post in REDDIT_OBJECT.get_saved_posts(username=REDDIT_OBJECT.get_reddit_username(), limit=LIMIT)]     
    item_list += get_folder_item_list(current_folder=CURRENT_FOLDER)
    print(len(item_list))
    return render_template('home.html', item_list=item_list)

@app.route('/new_folder', methods=['GET', 'POST'])
def new_folder():
    if CURRENT_FOLDER == get_root_folder_id(reddit_username=REDDIT_OBJECT.get_reddit_username()):
        return redirect(url_for('home'))

    if request.method == 'POST':
        if request.form['newfolderaction'] == 'create':
            folder_name = request.form['foldername']
            print(folder_name)
            REDDIT_SAVED_OBJECT.create_saved_folder(folder_name=folder_name, parent_folder_id=CURRENT_FOLDER, reddit_username=REDDIT_OBJECT.get_reddit_username())
        return redirect(url_for('home'))
    
    return render_template('newfolder.html')

@app.route('/playback/<post_id>')
def playback(post_id):
    post_object = REDDIT_OBJECT.get_post_object(post_id=post_id)
    media_url = REDDIT_OBJECT.get_media_url(post=post_object)[0]

    return render_template('playback.html', media_url=media_url)
