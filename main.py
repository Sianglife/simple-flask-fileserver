from flask import Flask, send_from_directory, render_template_string
import os

app = Flask(__name__)

FILE_DIR = './files'


@app.route('/')
def list_files():
    files = os.listdir(FILE_DIR)
    files = [f for f in files if os.path.isfile(os.path.join(FILE_DIR, f))]

    html = """
    <h1>目錄檔案清單</h1>
    <ul>
        {% for file in files %}
            <li><a href="/files/{{ file }}">{{ file }}</a></li>
        {% endfor %}
    </ul>
    """
    return render_template_string(html, files=files)


@app.route('/files/<path:filename>')
def download_file(filename):
    return send_from_directory(FILE_DIR, filename, as_attachment=False)


if __name__ == '__main__':
    app.run(debug=True)
