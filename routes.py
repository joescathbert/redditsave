from run import app
from flask import render_template, request, url_for, redirect, abort, flash
from dotenv import load_dotenv
import os
from models.redditposts import RedditModel
from models.redditsaved import RedditSavedModel

load_dotenv()

# User Global Variables
REDDIT_OBJECT = None
REDDIT_USERNAME = ''
REDDIT_SAVED_OBJECT = RedditSavedModel()
ROOT_FOLDER = 0
CURRENT_FOLDER = 0

CACHE_ITEM_LIST = []
CACHE_SAVED_ITEM_LIST = []
CACHE_COPY_ITEM_LIST = []
LIMIT = 500

###### Debug Functions

def print_all_global_variables():
    print(f'{REDDIT_USERNAME=}')
    print(f'{ROOT_FOLDER=}')
    print(f'{CURRENT_FOLDER=}')
    print(f'{CACHE_ITEM_LIST=}')
    print(f'{CACHE_SAVED_ITEM_LIST=}')
    print(f'{CACHE_COPY_ITEM_LIST=}')


######################


def get_folder_item_list(current_folder):
    saved_folders_list = REDDIT_SAVED_OBJECT.get_saved_folders(parent_folder_id=current_folder)
    return [{'id': saved_folder['item_id'], 'name': saved_folder['item_name'], 'type': saved_folder['item_type']} for saved_folder in saved_folders_list]

def get_post_item_list(current_folder):
    saved_posts_list = REDDIT_SAVED_OBJECT.get_saved_posts(parent_folder_id=current_folder)
    return [{'id': str(saved_post['item_id']), 'name': saved_post['item_name'], 'type': saved_post['item_type'], 'post_id': saved_post['item_post_id']} for saved_post in saved_posts_list]

def get_post_id_from_item_id(item_id):
    saved_post = REDDIT_SAVED_OBJECT.get_item(item_id=item_id)
    return str(saved_post['item_post_id'])

def get_folder_type(current_folder):
    folder = REDDIT_SAVED_OBJECT.get_item(item_id=current_folder)
    return folder['item_type']

def get_root_folder_id(reddit_username):
    user = REDDIT_SAVED_OBJECT.get_user(reddit_username=reddit_username)
    return user['root_item_id']

def do_up_folder(current_folder):
    folder = REDDIT_SAVED_OBJECT.get_item(item_id=current_folder)
    return folder['parent_item_id']

def do_paste_items(current_folder):
    global CACHE_COPY_ITEM_LIST
    for each_item_id in CACHE_COPY_ITEM_LIST:
        post_name = REDDIT_OBJECT.get_post_object(post_id=each_item_id).title
        REDDIT_SAVED_OBJECT.add_post(post_name=post_name, post_id=each_item_id, parent_folder_id=current_folder, reddit_username=REDDIT_USERNAME)
    CACHE_COPY_ITEM_LIST = []

def refresh_cache_item_list():
    global CACHE_ITEM_LIST
    # CACHE_ITEM_LIST = [{'name': post.title, 'id': post.id, 'type': 'post'} for post in REDDIT_OBJECT.get_saved_posts(username=REDDIT_USERNAME, limit=LIMIT)]
    # CACHE_ITEM_LIST = [{'name': post.title, 'id': post.id, 'type': 'post'} for post in REDDIT_OBJECT.get_search_posts(subreddit_name='', query="", sort="new", )]
    CACHE_ITEM_LIST = [{'name': post['title'], 'id': post['id'], 'type': 'post'} for post in REDDIT_OBJECT.get_posts_pushshiftapi(query='', subreddit='', author='')]
    

@app.before_request
def limit_remote_addr():
    if request.remote_addr not in ['192.168.0.105']:
        abort(403)

@app.route('/login', methods=['GET', 'POST'])
def login():
    global REDDIT_OBJECT
    if request.method == 'POST':
        if request.form['loginaction'] == 'login':
            REDDIT_OBJECT = RedditModel(client_id=os.environ['reddit_client_id'], client_secret=os.environ['reddit_client_secret'], 
                user_agent=os.environ['reddit_user_agent'])
            auth_url = REDDIT_OBJECT.get_auth_url()
            print(auth_url)
            return redirect(auth_url)

    return render_template('login.html')


@app.route('/', methods=['GET', 'POST'])
def home():
    global REDDIT_OBJECT, CURRENT_FOLDER, REDDIT_SAVED_OBJECT, REDDIT_USERNAME, ROOT_FOLDER, CACHE_ITEM_LIST, CACHE_SAVED_ITEM_LIST, CACHE_COPY_ITEM_LIST

    if not REDDIT_OBJECT:
        return redirect(url_for('login'))

    if request.method == 'GET':
        state = request.args.get('state')
        code = request.args.get('code')
        if code:
            REDDIT_OBJECT.authorize_app(code=code)
            REDDIT_USERNAME = REDDIT_OBJECT.get_reddit_username()
            REDDIT_SAVED_OBJECT.add_user(reddit_username=REDDIT_USERNAME)
            ROOT_FOLDER =  get_root_folder_id(reddit_username=REDDIT_USERNAME)  
            CURRENT_FOLDER = get_root_folder_id(reddit_username=REDDIT_USERNAME)
            print('################ User Initiated ####################')

    item_list = []

    utility_indicator = {'copy_item': CURRENT_FOLDER not in [ROOT_FOLDER, ROOT_FOLDER + 1, ROOT_FOLDER + 2], 
        'paste_item': len(CACHE_COPY_ITEM_LIST) != 0 and get_folder_type(current_folder=CURRENT_FOLDER) == 'user_folder', 'up_directory': CURRENT_FOLDER != ROOT_FOLDER, 
        'add_directory': get_folder_type(current_folder=CURRENT_FOLDER) == 'user_folder'}

    if request.method == 'POST':
        item_type = request.form['itemtype']
        item_id = request.form['itemid']
        print(item_id, item_type)

        if item_type in ['inbuilt_folder', 'user_folder'] :
            CURRENT_FOLDER = int(request.form['itemid'])
            return redirect(url_for('home'))

        if item_type == 'action' and CURRENT_FOLDER != ROOT_FOLDER:
            if item_id == 'nf' and get_folder_type(current_folder=CURRENT_FOLDER) == 'user_folder':
                return redirect(url_for('new_folder'))
            if item_id == 'uf':
                CURRENT_FOLDER = do_up_folder(current_folder=CURRENT_FOLDER)
                return redirect(url_for('home'))

        if item_type == 'action' and item_id == 'paste' and (len(CACHE_COPY_ITEM_LIST) != 0 and get_folder_type(current_folder=CURRENT_FOLDER) == 'user_folder'):
            do_paste_items(current_folder=CURRENT_FOLDER)
            return redirect(url_for('home'))

        if item_type == 'post':
            if CURRENT_FOLDER == ROOT_FOLDER + 1:
                return redirect(url_for('playback', post_id=item_id))
            else:
                return redirect(url_for('playback', post_item_id=item_id))

    print(CURRENT_FOLDER)
    if CURRENT_FOLDER == ROOT_FOLDER + 1:
        if not CACHE_ITEM_LIST:
            refresh_cache_item_list()
        item_list = CACHE_ITEM_LIST
    else:
        item_list += get_folder_item_list(current_folder=CURRENT_FOLDER)
        post_item_list = get_post_item_list(current_folder=CURRENT_FOLDER)
        item_list += post_item_list
        CACHE_SAVED_ITEM_LIST = post_item_list

    print(len(item_list))

    print(utility_indicator)

    print_all_global_variables()

    return render_template('home.html', item_list=item_list, utility_indicator=utility_indicator)

@app.route('/new_folder', methods=['GET', 'POST'])
def new_folder():
    if CURRENT_FOLDER == ROOT_FOLDER:
        return redirect(url_for('home'))

    if request.method == 'POST':
        if request.form['newfolderaction'] == 'create':
            folder_name = request.form['foldername']
            print(folder_name)
            REDDIT_SAVED_OBJECT.create_saved_folder(folder_name=folder_name, parent_folder_id=CURRENT_FOLDER, reddit_username=REDDIT_USERNAME)
        return redirect(url_for('home'))
    
    return render_template('newfolder.html')

@app.route('/playback', methods=['GET', 'POST'])
def playback():
    global CACHE_COPY_ITEM_LIST, CACHE_ITEM_LIST, CACHE_SAVED_ITEM_LIST

    post_item_id = request.args.get('post_item_id', None)
    post_id = request.args.get('post_id', None)
    print(post_item_id, post_id)

    if request.method == 'POST':
        item_type = request.form['itemtype']
        item_id = request.form['itemid']
        print(item_id, item_type)

        if item_id in ['pi', 'ni']:
            if post_id:
                cache_post_id_list = [c_i['id'] for c_i in CACHE_ITEM_LIST]
                current_index = cache_post_id_list.index(post_id)
                print(current_index, len(CACHE_ITEM_LIST))
                if item_id == 'pi' and current_index != 0:
                    post_id = CACHE_ITEM_LIST[current_index - 1]['id']
                    print(current_index - 1)
                elif item_id == 'ni' and current_index != len(CACHE_ITEM_LIST) - 1:
                    post_id = CACHE_ITEM_LIST[current_index + 1]['id']
                    print(current_index + 1)
            elif post_item_id:
                cache_post_id_list = [c_i['id'] for c_i in CACHE_SAVED_ITEM_LIST]
                print(CACHE_SAVED_ITEM_LIST, cache_post_id_list)
                current_index = cache_post_id_list.index(post_item_id)
                print(current_index, len(CACHE_SAVED_ITEM_LIST))
                if item_id == 'pi' and current_index != 0:
                    post_item_id = CACHE_SAVED_ITEM_LIST[current_index - 1]['id']
                    print(current_index - 1)
                elif item_id == 'ni' and current_index != len(CACHE_SAVED_ITEM_LIST) - 1:
                    post_item_id = CACHE_SAVED_ITEM_LIST[current_index + 1]['id']
                    print(current_index + 1)

        if item_id == 'copy':
            if post_id not in CACHE_COPY_ITEM_LIST:
                CACHE_COPY_ITEM_LIST.append(post_id)
                flash("This post has been added to clipboard.")
            else:
                CACHE_COPY_ITEM_LIST.pop(CACHE_COPY_ITEM_LIST.index(post_id))
                flash("This post has been removed from clipboard.")
            
        
        return redirect(url_for('playback', post_id=post_id, post_item_id=post_item_id))
    
    post_id = get_post_id_from_item_id(item_id=post_item_id) if not post_id else post_id
    post_object = REDDIT_OBJECT.get_post_object(post_id=post_id)
    media_url = REDDIT_OBJECT.get_media_url(post=post_object)[0]
    REDDIT_OBJECT.get_post_details(post=post_object)
    print(f'{media_url=}')
    print_all_global_variables()

    return render_template('playback.html', media_url=media_url)
