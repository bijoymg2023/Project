from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
import mysql.connector
from datetime import datetime

# Flask app initialization
app = Flask(__name__)
app.secret_key = 'super_secret_key'
bcrypt = Bcrypt(app)

# Database connection setup
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='root@1234',
        database='family_expense_tracker'
    )

# Helper function to execute queries
def execute_query(query, params=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def fetch_query(query, params=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results

# Function to calculate daily, monthly, and yearly expenses

def calculate_expenses(user_id):
    today = datetime.today()
    daily_expense = 0
    monthly_expense = 0
    yearly_expense = 0
    total_expense = 0

    expenses = fetch_query(""" 
        SELECT amount, expense_date FROM expenses WHERE user_id = %s
    """, (user_id,))

    for expense in expenses:
        # Ensure expense_date is a datetime object (if it's a string, convert it)
        expense_date = expense['expense_date']
        
        if isinstance(expense_date, datetime):
            # If it's already a datetime, just use it
            expense_date = expense_date.date()  # Get only the date part
        elif isinstance(expense_date, str):
            # If it's a string, parse it into a datetime object
            expense_date = datetime.strptime(expense_date, "%Y-%m-%d").date()

        amount = expense['amount']
        total_expense += amount
        
        # Compare only the date part with today's date
        if expense_date == today.date():
            daily_expense += amount

        if expense_date.month == today.month and expense_date.year == today.year:
            monthly_expense += amount

        if expense_date.year == today.year:
            yearly_expense += amount

    return {
        'daily': daily_expense,
        'monthly': monthly_expense,
        'yearly': yearly_expense,
        'total': total_expense
    }


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        role = request.form['role']

        query = "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)"
        try:
            execute_query(query, (username, email, password, role))
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('home'))
        except:
            flash('Error: Username or email already taken.', 'danger')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        user = fetch_query("SELECT * FROM users WHERE email = %s AND role = %s", (email, role))
        if user and bcrypt.check_password_hash(user[0]['password'], password):
            session['user_id'] = user[0]['user_id']
            session['username'] = user[0]['username']
            session['role'] = user[0]['role']
            if session['role'] == 'head':
                return redirect(url_for('dashboard_head'))
            else:
                return redirect(url_for('dashboard_member'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/dashboard_head')
def dashboard_head():
    if 'user_id' not in session or session['role'] != 'head':
        return redirect(url_for('login'))

    all_expenses = fetch_query("""
        SELECT e.expense_id, u.username, e.amount, e.expense_date, e.description, e.payment_method
        FROM expenses e
        JOIN users u ON e.user_id = u.user_id
        ORDER BY e.expense_date DESC
    """)
    
    personal_expenses = fetch_query("SELECT * FROM expenses WHERE user_id = %s", (session['user_id'],))
    return render_template('dashboard_head.html', username=session['username'], all_expenses=all_expenses, personal_expenses=personal_expenses)

@app.route('/dashboard_member')
def dashboard_member():
    if 'user_id' not in session or session['role'] != 'member':
        return redirect(url_for('login'))

    expenses = fetch_query("SELECT * FROM expenses WHERE user_id = %s", (session['user_id'],))
    return render_template('dashboard_member.html', username=session['username'], expenses=expenses, member=session['role'])

@app.route('/add_expense', methods=['POST', 'GET'])
def add_expense():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        amount = request.form['amount']
        expense_date = request.form['expense_date']
        description = request.form['description']
        payment_method = request.form['payment_method']

        query = '''
            INSERT INTO expenses (user_id, amount, expense_date, description, payment_method) 
            VALUES (%s, %s, %s, %s, %s)
        '''
        execute_query(query, (session['user_id'], amount, expense_date, description, payment_method))
        flash('Expense added successfully!', 'success')

        if session['role'] == 'head':
            return redirect(url_for('dashboard_head'))
        return redirect(url_for('dashboard_member'))

    return render_template('add_expense.html')

@app.route('/delete_expense/<int:expense_id>')
def delete_expense(expense_id):
    if 'user_id' in session:
        execute_query("DELETE FROM expenses WHERE expense_id = %s AND user_id = %s", (expense_id, session['user_id']))
        flash('Expense deleted successfully!', 'info')
    return redirect(url_for('dashboard_head') if session['role'] == 'head' else url_for('dashboard_member'))

@app.route('/summary')
def summary():
    # Redirect if the user is not logged in
    if 'user_id' not in session:
        return redirect(url_for('dashboard_head') if session.get('role') == 'head' else url_for('dashboard_member'))

    # Calculate expenses (assuming calculate_expenses is a helper function you've defined)
    expenses = calculate_expenses(session['user_id'])

    # Fetch the user info for display purposes
    member = {
        'username': session.get('username'),
        'role': session.get('role')
    }

    # Render template with expenses and member info
    return render_template('summary.html', expenses=expenses, member=member)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
