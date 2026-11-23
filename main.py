import os
import posixpath

from flask import Flask, abort, render_template_string, send_from_directory
from werkzeug.utils import safe_join

app = Flask(__name__)

FILE_DIR = os.path.abspath('./files')

TEMPLATE = """
<h1>目錄檔案清單 /{{ subpath }}</h1>
<ul>
    {% if subpath %}
        <li><a href="{{ url_for('browse', subpath=parent) }}">⬆ ..</a></li>
    {% endif %}
    {% for d in dirs %}
        <li>📁 <a href="{{ url_for('browse', subpath=join(subpath, d)) }}">{{ d }}/</a></li>
    {% endfor %}
    {% for f in files %}
        <li>📄 <a href="{{ url_for('download_file', filename=join(subpath, f)) }}">{{ f }}</a></li>
    {% endfor %}
</ul>
"""


@app.route('/', defaults={'subpath': ''})
@app.route('/browse/<path:subpath>')
def browse(subpath):
    # safe_join returns None if the path tries to escape FILE_DIR (e.g. "../")
    abs_path = safe_join(FILE_DIR, subpath)
    if abs_path is None or not os.path.isdir(abs_path):
        abort(404)

    dirs, files = [], []
    for name in sorted(os.listdir(abs_path), key=str.lower):
        full = os.path.join(abs_path, name)
        if os.path.isdir(full):
            dirs.append(name)
        elif os.path.isfile(full):
            files.append(name)

    subpath = subpath.strip('/')
    parent = posixpath.dirname(subpath)  # '' means root

    return render_template_string(
        TEMPLATE,
        subpath=subpath,
        parent=parent,
        dirs=dirs,
        files=files,
        join=lambda base, name: posixpath.join(base, name) if base else name,
    )


@app.route('/files/<path:filename>')
def download_file(filename):
    # send_from_directory also uses safe_join internally, so traversal is blocked
    return send_from_directory(FILE_DIR, filename, as_attachment=False)


if __name__ == '__main__':
    # debug=True together with host 0.0.0.0 exposes the Werkzeug debugger to the
    # network, which allows remote code execution. Enable it only when needed:
    #   FLASK_DEBUG=1 python main.py
    debug = os.environ.get('FLASK_DEBUG') == '1'
    app.run(host="0.0.0.0", debug=debug)
