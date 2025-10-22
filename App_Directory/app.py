from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DB_NAME = 'users.db'

def init_db():
    """Initialize the database if it doesn't exist."""
    if not os.path.exists(DB_NAME):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                username TEXT UNIQUE NOT NULL,
                                password TEXT NOT NULL
                              )''')
            conn.commit()
            print("✅ Database and users table created successfully.")


# ======================
# DATA
# ======================
milk_tea_options = [
    {"id": "MT001", "flavor": "Classic Milk Tea", "price": 4.50, "image": "milk.jpg"},
    {"id": "MT002", "flavor": "Taro Milk Tea", "price": 5.00, "image": "milk3.jpg"},
    {"id": "MT003", "flavor": "Matcha Milk Tea", "price": 5.50, "image": "milk4.jpg"},
    {"id": "MT004", "flavor": "Brown Sugar Milk Tea", "price": 5.00, "image": "brown_sugar.jpg"},
    {"id": "MT005", "flavor": "Honeydew Milk Tea", "price": 4.75, "image": "honeydew.jpg"}
]

sizes = ["Small", "Medium", "Large"]

# ======================
# ROUTES
# ======================

@app.route('/')
def home():
    return render_template('landing.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/menu')
def menu():
    if 'username' not in session:
        flash("Please log in first!")
        return redirect(url_for('login'))
    return render_template('index.html', milk_tea_options=milk_tea_options, sizes=sizes)

@app.route('/order', methods=['POST'])
def order():
    if 'username' not in session:
        flash("You must be logged in to place an order.")
        return redirect(url_for('login'))

    flavor = request.form.get('flavor')
    size = request.form.get('size')
    quantity = int(request.form.get('quantity'))
    price = next(item['price'] for item in milk_tea_options if item['flavor'] == flavor)
    total_price = price * quantity

    return render_template('order_summary.html',
                           flavor=flavor, size=size, quantity=quantity, total_price=total_price)

# ======================
# LOGIN & REGISTER
# ======================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                flash("Account created successfully! Please log in.")
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash("Username already exists! Try another.")
                return redirect(url_for('register'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = cursor.fetchone()

            if user:
                session['username'] = username
                flash("Login successful!")
                return redirect(url_for('menu'))
            else:
                flash("Invalid username or password!")
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out.")
    return redirect(url_for('home'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
