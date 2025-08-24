from flask import Flask, render_template, send_from_directory, abort
import os

app = Flask(__name__)

BASE_DIR = "/home/nipun/my_ansible_project"
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
BACKUPS_DIR = os.path.join(BASE_DIR, "backups")

@app.route("/")
def index():
    outputs = sorted(os.listdir(OUTPUTS_DIR))

    backups = {}
    for timestamp in sorted(os.listdir(BACKUPS_DIR), reverse=True):
        timestamp_path = os.path.join(BACKUPS_DIR, timestamp)
        if os.path.isdir(timestamp_path):
            backups[timestamp] = {}
            for subfolder in ['acc', 'dis', 'core']:
                sub_path = os.path.join(timestamp_path, subfolder)
                if os.path.isdir(sub_path):
                    backups[timestamp][subfolder] = sorted(os.listdir(sub_path))

    return render_template("index.html", outputs=outputs, backups=backups)

@app.route("/outputs/<path:filename>")
def serve_output_file(filename):
    try:
        return send_from_directory(OUTPUTS_DIR, filename, as_attachment=False)
    except:
        abort(404)

@app.route("/backups/<timestamp>/<subfolder>/<path:filename>")
def serve_backup_file(timestamp, subfolder, filename):
    folder_path = os.path.join(BACKUPS_DIR, timestamp, subfolder)
    try:
        return send_from_directory(folder_path, filename, as_attachment=True)
    except:
        abort(404)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
