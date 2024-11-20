from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
import os
import requests

app = Flask(__name__)

# Load environment variables
load_dotenv()
key = os.getenv("USER_KEY")
app.secret_key = os.getenv("SECRET_KEY")

# API base URL and headers
bible_version = "de4e12af7f28f599-01"  # King James
url = "https://api.scripture.api.bible/v1/bibles"
headers = {
    "accept": "application/json",
    "api-key": key,
}

# Helper Functions
def get_book(version, book):
    params = {
        "include-chapters": "true",
    }
    response = requests.get(f"{url}/{version}/books/{book}/chapters", headers=headers, params=params)
    return response.json()["data"]

def get_versions():
    params = {
        'language':'eng'
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()["data"]

def get_list_of_books(bible_version):
    response = requests.get(f"{url}/{bible_version}/books", headers=headers)
    return response.json()["data"]

def get_chapter_html(version, chapter_id):
    params = {
        "content-type": "html",
        "include-notes": "false",
        "include-titles": "true",
        "include-chapter-numbers": "true",
        "include-verse-numbers": "true",
        "include-verse-spans": "true",
    }
    response = requests.get(f"{url}/{version}/chapters/{chapter_id}", headers=headers, params=params)
    return response.json()["data"]

# Flask Routes
@app.route("/")
def choose_version():
    session["version_opt"]= {version["id"]: version["name"] for version in get_versions()}
    versions_list = [(version["id"], version["name"], version["description"]) for version in get_versions()]
    return render_template("choose_version.html", versions=versions_list)

@app.route("/bible/<string:version>")
def choose_book(version):
    books = get_list_of_books(version)
    session['books']={book["id"]: book["name"] for book in books}
    version_name = session["version_opt"][version]
    books_dict = [(book["id"], book["name"]) for book in books]
    return render_template("choose_book.html", books=books_dict, version=version, version_name=version_name)

@app.route("/bible/<string:version>/<string:book>")
def choose_chapter(version, book):
    book_name=session['books'][book]
    chapters = [(chapter["id"], chapter["number"]) for chapter in get_book(version, book)]
    return render_template("choose_chapter.html", chapters=chapters, version=version, book=book_name)

@app.route("/bible/<string:version>/chapter/<string:chapter_id>")
def get_chapter(version, chapter_id):
    chapter_data = get_chapter_html(version, chapter_id)
    
    book=chapter_id.split(".")[0]
    book_name=session['books'][book]
    
    next=chapter_data["next"]['id']
    previous=chapter_data["previous"]['id']
    
    return render_template("show_chapter.html",
                            version=version,
                            book=book,
                            book_name=book_name,
                            chapter=chapter_data["content"], 
                            next=chapter_data["next"]['id'], 
                            previous=chapter_data["previous"]['id'])

# Run Flask App
if __name__ == "__main__":
    app.run(debug=True)

l = "be8dc4ba39edf911-01"
p = "GEN"

# # with open('genKikuyu.txt', 'w', encoding="utf-8") as f:
#     # f.write(get_book(l, p))
# print(get_book(l, p))