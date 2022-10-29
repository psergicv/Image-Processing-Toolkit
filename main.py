from flask import Flask, render_template, request, flash, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from PIL import Image
import os

UPLOAD_FOLDER = "images"
DOWNLOAD_FOLDER = "converted_images"
ALLOWED_EXTENSIONS = {'jpg', 'png', 'webp', 'gif', 'jfif'}

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret_key_here"
app.config['TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        choice = request.form['choice']
        if choice == "JPG to PNG":
            return redirect(url_for('jpg_to_png_converter'))
        else:
            return "<h1>ERROR! You did something wrong!</h1>"
    return render_template("index.html")


@app.route('/jpg_to_png_converter', methods=['GET', 'POST'])
def jpg_to_png_converter():
    if request.method == "POST":
        if 'file' not in request.files:
            flash("No file part")
            return redirect(url_for('index'))
        file = request.files['file']
        if file.filename == "":
            flash("File not selected")
            return redirect(url_for("index"))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('converted_image', name=filename))
    return render_template('jpg_to_png.html')


@app.route('/converted_image/<name>')
def converted_image(name):
    image = Image.open(f"images/{name}")
    new_image_name = name.split(".")[0] + "_png"
    image.save(f"converted_images/{new_image_name}.png")
    return send_file(
        f'converted_images/{new_image_name}.png',
        mimetype='image/png',
        download_name=f'{new_image_name}.png',
        as_attachment=True
    )


if __name__ == '__main__':
    app.run(debug=True)
