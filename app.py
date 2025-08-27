from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import random, string

app = Flask(__name__)

# Database setup (SQLite file inside project folder)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.String(500), nullable=False)
    short_code = db.Column(db.String(6), unique=True, nullable=False)

# Generate random short code
def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Home page
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

# Shorten URL route
@app.route("/shorten", methods=["POST"])
def shorten():
    long_url = request.form.get("long_url")
    if not long_url:
        return redirect("/")  # redirect if input empty

    # Generate unique short code
    short_code = generate_short_code()
    while URL.query.filter_by(short_code=short_code).first():
        short_code = generate_short_code()

    # Save to database
    new_url = URL(long_url=long_url, short_code=short_code)
    db.session.add(new_url)
    db.session.commit()

    short_url = request.host_url + short_code
    return render_template("index.html", short_url=short_url, new_url = new_url)

# Redirect short URL to original URL
@app.route("/<short_code>")
def redirect_to_url(short_code):
    url = URL.query.filter_by(short_code=short_code).first()
    if url:
        return redirect(url.long_url)
    else:
        return "❌ Invalid short URL", 404

# History page
@app.route("/history")
def history():
    urls = URL.query.all()
    return render_template("history.html", urls=urls)

# Delete URL
@app.route("/delete/<int:url_id>", methods=["POST"])
def delete_url(url_id):
    url = URL.query.get_or_404(url_id)  # Get the URL by ID or return 404
    db.session.delete(url)
    db.session.commit()
    return redirect("/history")  # Go back to history page

# Edit URL
# Edit short code
@app.route("/edit/<int:url_id>", methods=["GET", "POST"])
def edit_short(url_id):
    url = URL.query.get_or_404(url_id)

    if request.method == "POST":
        new_short = request.form["short_code"].strip()
        # Check if new short code is unique
        if URL.query.filter_by(short_code=new_short).first():
            return "❌ Short code already exists!"

        url.short_code = new_short
        db.session.commit()

        # Redirect to home page after editing
        return redirect("/")

    return render_template("edit.html", url=url)




if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables if not exist
    app.run(debug=True)
