from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DB_NAME = 'users.db'

# ======================
# DATABASE INITIALIZATION
# ======================
def init_db():
    """Initialize database with proper structure (only once if not existing)."""
    if not os.path.exists(DB_NAME):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    contact TEXT NOT NULL,
                    gmail TEXT NOT NULL,
                    address TEXT NOT NULL,
                    zip TEXT NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            ''')
            conn.commit()
            print("✅ Database 'users.db' created successfully.")
    else:
        print("ℹ️ Database already exists. Skipping recreation.")


# ======================
# DATA
# ======================
milk_tea_options = [
    {"id": "MT001", "flavor": "Classic Milk Tea", "price": 4.50},
    {"id": "MT002", "flavor": "Taro Milk Tea", "price": 5.00},
    {"id": "MT003", "flavor": "Matcha Milk Tea", "price": 5.50},
    {"id": "MT004", "flavor": "Brown Sugar Milk Tea", "price": 5.00},
    {"id": "MT005", "flavor": "Honeydew Milk Tea", "price": 4.75}
]

sizes = ["Small", "Medium", "Large"]


# ======================
# ROUTES
# ======================
@app.route('/')
def landing():
    """Landing page (Home page)."""
    return render_template('landing.html')


@app.route('/menu')
def menu():
    """Menu page (replaces 'Home')."""
    if 'username' not in session:
        flash("⚠️ Please log in first!")
        return redirect(url_for('login'))
    return render_template('index.html', milk_tea_options=milk_tea_options, sizes=sizes)


@app.route('/about')
def about():
    """Accessible only when logged in."""
    if 'username' not in session:
        flash("⚠️ Please log in first!")
        return redirect(url_for('login'))
    return render_template('about.html')


@app.route('/contact')
def contact():
    """Accessible only when logged in."""
    if 'username' not in session:
        flash("⚠️ Please log in first!")
        return redirect(url_for('login'))
    return render_template('contact.html')


# ======================
# CART & ORDER SUMMARY
# ======================
@app.route('/cart')
def cart():
    if 'username' not in session:
        flash("⚠️ Please log in first!")
        return redirect(url_for('login'))
    return render_template('Cart.html')


@app.route('/order_summary')
def order_summary():
    if 'username' not in session:
        flash("⚠️ Please log in first!")
        return redirect(url_for('login'))
    return render_template('order_summary.html')


@app.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == 'POST':
        if 'username' not in session:
            flash("⚠️ You must be logged in to place an order.")
            return redirect(url_for('login'))

        flavor = request.form.get('flavor')
        size = request.form.get('size')
        quantity = int(request.form.get('quantity'))
        payment = request.form.get('payment')

        price = next(item['price'] for item in milk_tea_options if item['flavor'] == flavor)
        total_price = price * quantity

        return render_template(
            'order_summary.html',
            flavor=flavor,
            size=size,
            quantity=quantity,
            total_price=total_price,
            payment=payment
        )

    return redirect(url_for('cart'))


# ======================
# REGISTER
# ======================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        gmail = request.form['gmail']
        address = request.form['address']
        zip_code = request.form['zip']
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=?", (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash("⚠️ Username already exists.")
                return redirect(url_for('register'))

            cursor.execute('''
                INSERT INTO users (name, contact, gmail, address, zip, username, password)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, contact, gmail, address, zip_code, username, password))
            conn.commit()

        flash("✅ Registration successful! Please log in.")
        return redirect(url_for('login'))

    return render_template('register.html')


# ======================
# LOGIN
# ======================
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
            flash("🎉 Login successful!")
            return redirect(url_for('menu'))
        else:
            flash("❌ Invalid username or password!")

    return render_template('login.html')


# ======================
# LOGOUT
# ======================
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("👋 You have been logged out.")
    return redirect(url_for('landing'))


# ======================
# MAIN ENTRY POINT
# ======================
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
