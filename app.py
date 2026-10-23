 
import os
import random
import string
import time
import threading

from flask import Flask, request,send_file,render_template

app = Flask(__name__) # creating a Flask application

#config
UPLOAD_FOLDER = 'uploads'   #varible is created uploaded files are stored
os.makedirs(UPLOAD_FOLDER,exist_ok=True) #if not exists creates one

app.config['MAX_CONTENT_LENGTH'] = 25*1024*1024 #size 25MB
LINK_EXPIRY = 15*60 #expiry time

'''
your_project/
├── app.py
└── uploads/
    ├── photo.jpg
    └── notes.pdf
'''
'''
file_link = {
    "abc123": {
        "path": "uploads/photo.jpg",
        "time": 1792300000
    }
}
'''
file_link = {} #actual data struture 
               #creates a empty dict to store key value pair

def generate_random_string(length = 8):
    return''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route('/', methods=['GET','POST'])
def home():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', link=None, error='no file found')
        file = request.files['file']
        #save file
        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        random_id = generate_random_string()
        file_link[random_id] = {
            'path':filepath,
            'time':time.time()
        }

        share_link = request.host_url + random_id

        return render_template('index.html',link=share_link, error=None)
    
    return render_template('index.html')

@app.route('/<random_id>')
def download(random_id):
    get_file = file_link.get(random_id)

    if not get_file:
        return 'invalid or expired link'
    return send_file(get_file['path'],as_attachment=True)

def clean_up_file():
    while True:
        now = time.time()
        expired_keys = []

        for key,info in list(file_link.items()):
            if now - info['time'] > LINK_EXPIRY:
                try:
                    os.remove(info['path'])
                except:
                    pass
                expired_keys.append(key)
        # remove expired entries
        for key in expired_keys:
            del file_link[key]
        time.sleep(60)
threading.Thread(target=clean_up_file, daemon=True).start()

if __name__ == '__main__':   #actual starts the server
    app.run(debug=True)
#app.run() starts the server.
#debug=True enables helpful error messages and automatic reloading when code changes.

