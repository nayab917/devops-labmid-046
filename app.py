import json
import os
from urllib.parse import urlparse

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
app.config["DATA_FILE"] = os.environ.get("DATA_FILE", "submissions.json")

FIELDS = ["name", "reg_no", "title", "url"]


def load_submissions():
    path = app.config["DATA_FILE"]
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_submissions(items):
    with open(app.config["DATA_FILE"], "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)


def is_valid_url(url):
    parts = urlparse(url)
    return parts.scheme in ("http", "https") and "." in parts.netloc


def validate(form):
    errors = []
    if not form.get("name"):
        errors.append("Name is required.")
    if not form.get("title"):
        errors.append("Assignment title is required.")
    if not form.get("url"):
        errors.append("Submission URL is required.")
    elif not is_valid_url(form["url"]):
        errors.append("Submission URL is not valid. It must start with http:// or https://")
    return errors


@app.route("/", methods=["GET", "POST"])
def index():
    errors = []
    form = {}
    if request.method == "POST":
        form = {f: request.form.get(f, "").strip() for f in FIELDS}
        errors = validate(form)
        if not errors:
            items = load_submissions()
            items.append(form)
            save_submissions(items)
            return redirect(url_for("index", saved=1))
    return render_template(
        "index.html",
        submissions=load_submissions(),
        errors=errors,
        form=form,
        saved=request.args.get("saved"),
    )


if __name__ == "__main__":
    app.run(debug=True)
