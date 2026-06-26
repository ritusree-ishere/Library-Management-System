
import uuid
from werkzeug.security import generate_password_hash
from flask import Flask, render_template, request, redirect, session
from firebase_config import db
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash


app = Flask(__name__)
app.secret_key = "secretkey@123"
app.permanent_session_lifetime = timedelta(minutes=60)


# 🔐 Check login
def check_login():
    return session.get("user") is not None


def is_admin():
    return session.get("role") == "admin"


# 🏠 HOME PAGE
@app.route("/")
def index():
    if not check_login():
        return redirect("/login")

    books = []

   # ✅ Everyone sees all books
    docs = db.collection("books").stream()

    for doc in docs:
        data = doc.to_dict()

        data["id"] = doc.id
        data["rating"] = data.get("rating", 1)
        data["available"] = data.get("available", True)
        data["issued_to"] = data.get("issued_to", None)
        data["due_date"] = data.get("due_date", None)

        books.append(data)

    return render_template(
        "index.html",
        books=books,
        now=datetime.now(timezone.utc)
    )


# ➕ ADD BOOK
@app.route("/add", methods=["GET", "POST"])
def add():
    if not check_login():
        return redirect("/login")
    
    if session.get("role") != "admin":
        return "Access Denied", 403

    if request.method == "POST":
        db.collection("books").add({
            "title": request.form["title"],
            "author": request.form["author"],
            "price": float(request.form["price"]),
            "rating": int(request.form.get("rating", 1)),
            "available": True,
            "issued_to": None,
            "due_date": None,
        })
        return redirect("/")

    return render_template("add.html")


# 📚 ISSUE BOOK
@app.route("/issue/<id>")
def issue_book(id):
    if not check_login():
        return redirect("/login")

    doc_ref = db.collection("books").document(id)
    doc = doc_ref.get()

    if not doc.exists:
        return "Book not found", 404

    book = doc.to_dict()

    if not book.get("available", True):
        return "Book already issued", 400

    # ✅ FIXED (timezone-aware)
    due_date = datetime.now(timezone.utc) + timedelta(days=7)

    doc_ref.update({
        "available": False,
        "issued_to": session["user"],
        "due_date": due_date
    })

    return redirect("/")


# 📖 RETURN BOOK
@app.route("/return/<id>")
def return_book(id):
    if not check_login():
        return redirect("/login")

    doc_ref = db.collection("books").document(id)
    doc = doc_ref.get()

    if not doc.exists:
        return "Book not found", 404

    book = doc.to_dict()

    if book.get("issued_to") != session["user"]:
        return "Not your book", 403

    doc_ref.update({
        "available": True,
        "issued_to": None,
        "due_date": None
    })

    return redirect("/")


# ✏️ EDIT BOOK
@app.route("/edit/<id>", methods=["GET", "POST"])
def edit(id):
    if not check_login():
        return redirect("/login")

    doc_ref = db.collection("books").document(id)
    doc = doc_ref.get()

    if not doc.exists:
        return "Book not found", 404

    book = doc.to_dict()

    if session.get("role") != "admin":
        return "Access Denied", 403

    if request.method == "POST":
        doc_ref.update({
            "title": request.form["title"],
            "author": request.form["author"],
            "price": float(request.form["price"]),
            "rating": int(request.form.get("rating", 1))
        })
        return redirect("/")

    book["rating"] = book.get("rating", 1)

    return render_template("edit.html", book=book, id=id)


# ❌ DELETE BOOK
@app.route("/delete/<id>")
def delete(id):
    if not check_login():
        return redirect("/login")

    doc_ref = db.collection("books").document(id)
    doc = doc_ref.get()

    if not doc.exists:
        return "Book not found", 404

    book = doc.to_dict()

    # ✅ Allow admin OR owner
    if session.get("role") != "admin":
        return "Access Denied", 403

    doc_ref.delete()

    # ✅ Redirect properly
    if session.get("role") == "admin":
        return redirect("/admin")

    return redirect("/")


# 🔐 LOGIN
from werkzeug.security import check_password_hash

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_ref = db.collection("users").document(username).get()

        if not user_ref.exists:
            return render_template("login.html", error="User not found")

        user_data = user_ref.to_dict()

        if not check_password_hash(user_data["password"], password):
            return render_template("login.html", error="Wrong password")

        session.clear()
        session.permanent = True
        session["user"] = username
        session["role"] = user_data.get("role", "user")   # 🔥 IMPORTANT

        if user_data.get("role") == "admin":
            return redirect("/admin")

        return redirect("/")

    return render_template("login.html")


# 🔓 LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# 👤 ACCOUNT
@app.route("/account")
def account():
    if not check_login():
        return redirect("/login")

    return render_template("account.html", user=session["user"])


# 🆕 SIGNUP
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not username or not password:
            return render_template("signup.html", error="All fields required")

        user_ref = db.collection("users").document(username).get()

        if user_ref.exists:
            return render_template("signup.html", error="User already exists")

        hashed_password = generate_password_hash(password)

        # 👇 DEFAULT ROLE = user
        db.collection("users").document(username).set({
            "username": username,
            "password": hashed_password,
            "role": "user"
        })

        session["user"] = username
        session["role"] = "user"

        return redirect("/")

    return render_template("signup.html")


# 📚 MY BOOKS
@app.route("/my-books")
def my_books():
    if not check_login():
        return redirect("/login")

    books = []

    # ✅ Admin sees all issued books
    if session.get("role") == "admin":
        docs = db.collection("books").where(
            "available", "==", False
        ).stream()

    # ✅ Normal users see only their borrowed books
    else:
        docs = db.collection("books").where(
            "issued_to", "==", session["user"]
        ).stream()

    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        books.append(data)

    return render_template("my_books.html", books=books)


# 🛠 RESET LIBRARY
@app.route("/reset-library")
def reset_library():
    docs = db.collection("books").stream()

    for doc in docs:
        db.collection("books").document(doc.id).set({
            "available": True,
            "issued_to": None,
            "due_date": None
        }, merge=True)

    return "Library reset successful ✅"


# 🔄 RESET SESSION
@app.route("/reset-session")
def reset_session():
    session.clear()
    return "Session cleared"


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = request.form["username"]

        user_ref = db.collection("users").document(username)
        user = user_ref.get()

        if not user.exists:
            return render_template("forgot_password.html", error="User not found")

        # 🔑 Generate token
        token = str(uuid.uuid4())

        user_ref.update({
            "reset_token": token
        })

        # 👉 Show reset link (since no email system)
        reset_link = f"http://127.0.0.1:5000/reset-password/{token}"

        return render_template("forgot_password.html", message=reset_link)

    return render_template("forgot_password.html")


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    users = db.collection("users").stream()

    user_doc = None

    for doc in users:
        data = doc.to_dict()
        if data.get("reset_token") == token:
            user_doc = doc
            break

    if not user_doc:
        return "Invalid or expired token", 400

    if request.method == "POST":
        new_password = request.form["password"]

        hashed = generate_password_hash(new_password)

        db.collection("users").document(user_doc.id).update({
            "password": hashed,
            "reset_token": None
        })

        return redirect("/login")

    return render_template("reset_password.html")


@app.route("/admin")
def admin_dashboard():
    if not check_login():
        return redirect("/login")

    if session.get("role") != "admin":
        return "Access Denied", 403

    users = []
    books = []

    # 👥 Get users
    user_docs = db.collection("users").stream()
    for doc in user_docs:
        users.append(doc.to_dict())

    # 📚 Get books
    book_docs = db.collection("books").stream()
    for doc in book_docs:
        data = doc.to_dict()
        data["id"] = doc.id
        books.append(data)

    return render_template("admin.html", users=users, books=books)


if __name__ == "__main__":
    app.run(debug=True)