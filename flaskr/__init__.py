from flask import (
    Flask, render_template, request, jsonify
)
import os
from werkzeug.utils import secure_filename
import glob
from . import main

app = Flask(__name__)

IMAGES_FOLDER = 'flaskr/images'
app.config['IMAGES_FOLDER'] = IMAGES_FOLDER
INSPIRING_POEMS_FOLDER = 'flaskr/inspiring_poems'
GENERATED_POEMS_FOLDER = 'flaskr/generated_poems'

for folder in [IMAGES_FOLDER, INSPIRING_POEMS_FOLDER, GENERATED_POEMS_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

ALLOWED_TYPES = ['jpg', 'jpeg', 'png']

def allowed_file(filename):
    # Check if the file has a valid extension
    if '.' not in filename:
        return False
    name_split = filename.split('.', 1)
    extension = name_split[1].lower()
    return extension in ALLOWED_TYPES

@app.route("/", methods=["GET"])
def hello():
    for filename in glob.glob(f"{IMAGES_FOLDER}/*"): 
        os.remove(filename)
    for filename in glob.glob(f"{INSPIRING_POEMS_FOLDER}/*"):
        os.remove(filename)
    main.parse_poem_csv()
    return render_template('website.html')

@app.route("/upload", methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'files' not in request.files:
            return render_template('website.html', \
                                   files_uploaded = 'No file part')
        # file = request.files['file']
        files = request.files.getlist('files')
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if len(files) == 0:
        # if file.filename == '':
            return render_template('website.html', \
                               files_uploaded = 'No file selected. Try again.')
            # return redirect(url_for('hello'))
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['IMAGES_FOLDER'], filename))
        return render_template('website.html', \
                               files_uploaded = 'Files uploaded successfully!')
    return ''


@app.route('/generate', methods=['POST'])
def process_button_click():
    poem_tuple = main.main()
    poem_name = poem_tuple[0]
    new_poem = poem_tuple[1]
    if not new_poem == "*NO IMAGES*":
        filename = secure_filename(poem_name)
        file_path = f'{GENERATED_POEMS_FOLDER}/{filename}.txt'
        new_file = open(file_path, 'w')
        new_file.write(new_poem)
        new_file.close()
    poem_data = {'name' : poem_name, 'poem' : new_poem}
    return jsonify(poem_data)

@app.route('/history', methods=["POST"])
def view_old_poems():
    path_len = len(GENERATED_POEMS_FOLDER) + 1
    file_to_poem = dict()
    for filename in glob.glob(f"{GENERATED_POEMS_FOLDER}/*"): 
        poem_file = open(filename)
        poem_str = poem_file.read()
        file_to_poem[filename[path_len:-4]] = poem_str
    return jsonify(file_to_poem)