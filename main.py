from flask import Flask, render_template, request
import smtplib
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Fetch email and password from environment variables
OWN_EMAIL = os.getenv("OWN_EMAIL")
OWN_PASSWORD = os.getenv("OWN_PASSWORD")
NPOINT = os.getenv("NPOINT")

# Fetch blog posts with error handling
try:
    response = requests.get(NPOINT)
    response.raise_for_status()
    posts = response.json()
except requests.exceptions.RequestException as e:
    print(f"Error fetching posts: {e}")
    posts = []  # Fallback to an empty list or handle as appropriate

app = Flask(__name__)

@app.route('/')
def get_recent_posts():
    # Check if the length of posts is less than or equal to 3
    if len(posts) <= 3:
        recent_posts = posts  # Extract all posts
    else:
        recent_posts = posts[:3]  # Extract the three most recent posts
    return render_template("index.html", all_posts=recent_posts)

@app.route("/posts/all")
def get_all_posts():
    return render_template("all_posts.html", all_posts=posts)

@app.route("/post/<int:index>")
def show_post(index):
    requested_post = next((post for post in posts if post["id"] == index), None)
    return render_template("post.html", post=requested_post)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        data = request.form
        try:
            send_email(data["name"], data["email"], data["phone"], data["message"])
            return render_template("contact.html", msg_sent=True)
        except Exception as e:
            print(f"Error sending email: {e}")
            return render_template("contact.html", msg_sent=False, error=str(e))
    return render_template("contact.html", msg_sent=False)

def send_email(name, email, phone, message):
    email_message = f"Subject: New Message\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}"
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()
            connection.login(OWN_EMAIL, OWN_PASSWORD)
            connection.sendmail(OWN_EMAIL, OWN_EMAIL, email_message)
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise

if __name__ == "__main__":
    app.run(debug=True)
