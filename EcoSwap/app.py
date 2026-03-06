from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "ecoswap_secret_key"

# =========================
# DATABASE CREATION
# =========================
conn = sqlite3.connect("ecoswap.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    email TEXT,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    product_name TEXT,
    description TEXT,
    image TEXT,
    location TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS swap_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requester_id INTEGER,
    owner_id INTEGER,
    product_id INTEGER,
    status TEXT DEFAULT 'Pending'
)
""")

conn.commit()
conn.close()

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return render_template("home.html")

# =========================
# REGISTER
# =========================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        conn = sqlite3.connect("ecoswap.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, password)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("ecoswap.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):
            session["user_id"] = user[0]
            session["username"] = user[1]
            return redirect("/dashboard")
        else:
            return "Invalid Credentials ❌"

    return render_template("login.html")
# =========================
# DASHBOARD
# =========================
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("ecoswap.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT product_name, description FROM products WHERE user_id=?",
        (session["user_id"],)
    )
    products = cursor.fetchall()
    conn.close()

    return render_template(
        "dashboard.html",
        username=session["username"],
        products=products
    )

# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# =========================
# ADD PRODUCT
# =========================
@app.route("/add_product", methods=["GET", "POST"])
def add_product():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        product_name = request.form["product_name"]
        description = request.form["description"]

        conn = sqlite3.connect("ecoswap.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO products (user_id, product_name, description) VALUES (?, ?, ?)",
            (session["user_id"], product_name, description)
        )

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("add_product.html")

# =========================
# MARKETPLACE
# =========================
@app.route("/marketplace")
def marketplace():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("ecoswap.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT products.id, products.product_name, products.description, users.username
        FROM products
        JOIN users ON products.user_id = users.id
        WHERE products.user_id != ?
    """, (session["user_id"],))

    products = cursor.fetchall()
    conn.close()

    return render_template("marketplace.html", products=products)

# =========================
# REQUEST SWAP
# =========================
@app.route("/request_swap/<int:product_id>")
def request_swap(product_id):
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("ecoswap.db")
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM products WHERE id=?", (product_id,))
    owner = cursor.fetchone()

    if owner:
        owner_id = owner[0]

        cursor.execute("""
            INSERT INTO swap_requests (requester_id, owner_id, product_id)
            VALUES (?, ?, ?)
        """, (session["user_id"], owner_id, product_id))

        conn.commit()

    conn.close()
    return redirect("/marketplace")

# =========================
# VIEW SWAP REQUESTS (PROFESSIONAL TABLE DATA)
# =========================
@app.route("/swap_requests")
def swap_requests():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("ecoswap.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            swap_requests.id,
            products.product_name,
            users.username,
            swap_requests.status
        FROM swap_requests
        JOIN products ON swap_requests.product_id = products.id
        JOIN users ON swap_requests.requester_id = users.id
        WHERE swap_requests.owner_id = ?
    """, (session["user_id"],))

    requests = cursor.fetchall()
    conn.close()

    return render_template("swap_requests.html", requests=requests)

# =========================
# ACCEPT REQUEST
# =========================
@app.route("/accept_request/<int:request_id>")
def accept_request(request_id):
    conn = sqlite3.connect("ecoswap.db")
    cursor = conn.cursor()

    cursor.execute("SELECT product_id FROM swap_requests WHERE id=?", (request_id,))
    product = cursor.fetchone()

    if product:
        product_id = product[0]

        cursor.execute(
            "UPDATE swap_requests SET status='Accepted' WHERE id=?",
            (request_id,)
        )

        cursor.execute(
            "DELETE FROM products WHERE id=?",
            (product_id,)
        )

    conn.commit()
    conn.close()

    return redirect("/swap_requests")

# =========================
# REJECT REQUEST
# =========================
@app.route("/reject_request/<int:request_id>")
def reject_request(request_id):
    conn = sqlite3.connect("ecoswap.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE swap_requests SET status='Rejected' WHERE id=?",
        (request_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/swap_requests")

# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(debug=True)