import base64
import time
from flask import Flask, render_template, request
from flask_pymongo import MongoClient
import gridfs

app = Flask(__name__)

client = MongoClient('mongodb://vijayalb:Scooby2014*@ds117821.mlab.com:17821/vijayalakshmi')
current_user = None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    global current_user
    users = client.vijayalakshmi.users
    login_user = users.find_one({'name': request.form['user']})
    password = request.form['pass']
    if login_user:
        if password == login_user['password']:
            current_user = login_user
            return render_template('home.html')
    return 'Invalid Username/Password'


@app.route('/register', methods=['POST', 'GET'])
def register():
    users = client.vijayalakshmi.users
    existing_user = users.find_one({'name': request.form['newuser']})
    if existing_user is None:
        users.insert({'name': request.form['newuser'], 'password': request.form['newpass']})
        return render_template('index.html')
    return 'Username already exists'


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    global current_user
    image_file = request.files['pic']
    file_name = image_file.filename
    target = image_file.read()
    comments = request.form['comments']
    size = request.form['size']
    print (len(target))
    print (int(size))
    if len(target) < int(size):
        fs = gridfs.GridFS(client.vijayalakshmi)
        fs.put(target, filename=file_name, user=current_user, comment=comments)
        return render_template('home.html')
    return "File size exceeded!"


@app.route('/show', methods=['POST', 'GET'])
def display_mine():
    fs = gridfs.GridFS(client.vijayalakshmi)
    dictionary_list = []
    user_count = request.form['count']
    search_key = str(request.form['search_key'])
    count = 1
    start_time_all = time.time()
    for item in client.vijayalakshmi.fs.files.find({"user": current_user}):
        if count <= int(user_count):
            start_time = time.time()
            com = None
            file_name = item['filename']
            if 'comment' in item.keys():
                com = item['comment']
            if search_key in com:
                picture = fs.find_one({"filename": file_name}).read()
                picture_data = "data:image/jpeg;base64," + base64.b64encode(picture)
                end_time = time.time() - start_time
                variables = {'file_name': file_name, 'com': com, 'image': picture_data, 'time': end_time}
                dictionary_list.append(variables)
            count += 1
    end_time_all = time.time() - start_time_all
    return render_template('home.html', lists=dictionary_list, time=end_time_all)


@app.route('/showall', methods=['POST', 'GET'])
def display_all():
    fs = gridfs.GridFS(client.vijayalakshmi)
    dictionary_list = []
    for item in client.vijayalakshmi.fs.files.find():
        file_name = item['filename']
        if 'user' in item.keys():
            user_name = item['user']
        if 'comment' in item.keys():
            com = item['comment']
        picture = fs.find_one({"filename": file_name}).read()
        picture_data = "data:image/jpeg;base64," + base64.b64encode(picture)
        variables = {'user': user_name, 'file_name': file_name, 'com': com, 'image': picture_data}
        dictionary_list.append(variables)

    return render_template("home.html", alllist=dictionary_list)


@app.route('/delete', methods=['POST', 'GET'])
def delete():
    name = request.form['images']
    c = client.vijayalakshmi.fs.files
    c.delete_one({"filename": name})
    return render_template('home.html')


if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True)

