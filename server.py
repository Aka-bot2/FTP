import os
from flask import Flask, request, redirect, url_for, send_from_directory, render_template, session

# Config
UPLOAD_FOLDER = "shared_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = "supersecretkey"  # change this!

# Simple credentials
USERNAME = "akashh"
PASSWORD = "1234"

# ---- ROUTES ----

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == USERNAME and request.form["password"] == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/files")
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    files = os.listdir(app.config["UPLOAD_FOLDER"])
    return render_template("index.html", files=files)

# ---- NEW CHUNKED UPLOAD ----
@app.route("/upload_chunk", methods=["POST"])
def upload_chunk():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    file = request.files["file"]
    chunk_index = int(request.form["chunkIndex"])
    total_chunks = int(request.form["totalChunks"])
    filename = request.form["filename"]

    temp_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{filename}.part")

    # Append chunk to temp file
    with open(temp_path, "ab") as f:
        f.write(file.read())

    # If last chunk → rename to final file
    if chunk_index + 1 == total_chunks:
        final_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        os.rename(temp_path, final_path)

    return "OK"

# ---- OLD UPLOAD DISABLED ----
# @app.route("/upload", methods=["POST"])
# def upload_file():
#     if not session.get("logged_in"):
#         return redirect(url_for("login"))
#     if "file" not in request.files:
#         return redirect(url_for("index"))
#     file = request.files["file"]
#     if file.filename == "":
#         return redirect(url_for("index"))
#     filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
#     file.save(filepath)
#     return redirect(url_for("index"))

@app.route("/download/<path:filename>")
def download_file(filename):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
