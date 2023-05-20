from flask import Flask, render_template, request, flash, redirect, url_for, send_file, after_this_request
from werkzeug.utils import secure_filename
from PIL import Image
import os

UPLOAD_FOLDER = "images"
DOWNLOAD_FOLDER = "converted_images"
ALLOWED_EXTENSIONS = {'jpg', 'png', 'webp', 'jfif', 'bmp', 'svg', 'avif'}

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret_key_here"
app.config['TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/image_convert', methods=['GET', 'POST'])
def jpg_to_png_converter():
    if request.method == "POST":
        if 'file' not in request.files:
            flash("No file part")
            return redirect(url_for('image_convert_page'))
        file = request.files['file']
        if file.filename == "":
            flash("File not selected")
            return redirect(url_for("image_convert_page"))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('converted_image', name=filename))
    return render_template('jpg_to_png.html')


@app.route('/converted_image/<name>')
def converted_image(filename):
    try:
        image = Image.open(f"{app.config['UPLOAD_FOLDER']}/{filename}")
        new_image_name = os.path.splitext(filename)[0] + "_png"
        new_image_path = f"{app.config['DOWNLOAD_FOLDER']}/{new_image_name}.png"
        image.save(new_image_path)

        @after_this_request
        def delete_file(response):
            try:
                os.remove(new_image_path)
            except Exception as error:
                app.logger.error("Error removing or closing downloaded file handle", error)
            return response

        return send_file(
            new_image_path,
            mimetype='image/png',
            download_name=f'{new_image_name}.png',
            as_attachment=True
        )
    except Exception as e:
        return f"An error occurred: {e}"


if __name__ == '__main__':
    app.run(debug=True)
