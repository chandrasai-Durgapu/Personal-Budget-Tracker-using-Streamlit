import sqlite3
import bcrypt
import datetime

DB_FILE = 'budget_tracker.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# --- Table Creation Functions ---
def create_user_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def create_categories_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category_name TEXT NOT NULL,
            category_type TEXT NOT NULL,
            UNIQUE(user_id, category_name),
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

def create_transactions_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category_id INTEGER,
            amount REAL NOT NULL,
            transaction_date TEXT NOT NULL,
            note TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

def create_budgets_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            budget_amount REAL NOT NULL,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            category_id INTEGER,
            UNIQUE(user_id, category_id, month, year),
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

def initialize_database():
    """Call all table creation functions to set up the database."""
    create_user_table()
    create_categories_table()
    create_transactions_table()
    create_budgets_table()

# --- User Management ---
def create_user(username, password):
    conn = get_db_connection()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password.decode('utf-8')))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id

def authenticate_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return user
    return None

def get_username_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def set_default_categories(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    default_categories = [
        ('Groceries', 'expense'), ('Bills', 'expense'), ('Rent', 'expense'),
        ('Salary', 'income'), ('Freelance', 'income'),
        ('Savings', 'savings')
    ]
    
    for cat_name, cat_type in default_categories:
        cursor.execute("INSERT INTO categories (user_id, category_name, category_type) VALUES (?, ?, ?)", (user_id, cat_name, cat_type))
    
    conn.commit()
    conn.close()

# --- Category Management ---
def add_category(user_id, category_name, category_type):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO categories (user_id, category_name, category_type) VALUES (?, ?, ?)", (user_id, category_name, category_type))
    conn.commit()
    conn.close()

def update_category(category_id, new_name, new_type):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE categories SET category_name = ?, category_type = ? WHERE id = ?", (new_name, new_type, category_id))
    conn.commit()
    conn.close()

def delete_category(category_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE category_id = ?", (category_id,))
    cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    conn.commit()
    conn.close()

def get_user_categories(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, category_name, category_type FROM categories WHERE user_id = ? ORDER BY category_name ASC", (user_id,))
    categories = cursor.fetchall()
    conn.close()
    return [tuple(row) for row in categories]

# --- Transaction Management ---
def add_transaction(user_id, category_id, amount, date, note):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transactions (user_id, category_id, amount, transaction_date, note) VALUES (?, ?, ?, ?, ?)", (user_id, category_id, amount, date, note))
    conn.commit()
    conn.close()

def update_transaction(transaction_id, category_id, amount, date, note):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE transactions SET category_id = ?, amount = ?, transaction_date = ?, note = ? WHERE id = ?", (category_id, amount, date, note, transaction_id))
    conn.commit()
    conn.close()

def delete_transaction(transaction_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
    conn.commit()
    conn.close()

def fetch_transaction_history(user_id, start_date=None, end_date=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT t.id, t.transaction_date, c.category_name, c.category_type, t.amount, t.note 
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ?
    """
    params = [user_id]
    
    if start_date and end_date:
        query += " AND t.transaction_date BETWEEN ? AND ?"
        params.extend([start_date, end_date])
    
    query += " ORDER BY t.transaction_date DESC"
    
    cursor.execute(query, params)
    transactions = cursor.fetchall()
    conn.close()
    return [tuple(row) for row in transactions]

def get_transaction_by_id(transaction_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category_id, amount, transaction_date, note FROM transactions WHERE id = ?", (transaction_id,))
    transaction = cursor.fetchone()
    conn.close()
    return tuple(transaction) if transaction else None

# --- Budget Management ---
def set_budget(user_id, category_id, month, year, amount):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO budgets (user_id, category_id, budget_amount, month, year)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, category_id, amount, month, year))
    conn.commit()
    conn.close()

def get_budgets_for_month(user_id, month, year):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.id, b.user_id, b.budget_amount, b.category_id, c.category_name
        FROM budgets b
        JOIN categories c ON b.category_id = c.id
        WHERE b.user_id = ? AND b.month = ? AND b.year = ?
    """, (user_id, month, year))
    budgets = cursor.fetchall()
    conn.close()
    return [tuple(row) for row in budgets]

def get_total_spent_per_category(user_id, month, year):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.category_name, SUM(t.amount) as total_spent
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ? AND c.category_type = 'expense'
        AND strftime('%m', t.transaction_date) = ? AND strftime('%Y', t.transaction_date) = ?
        GROUP BY c.id
    """, (user_id, f'{month:02}', str(year)))
    
    spent_data = cursor.fetchall()
    conn.close()
    return [tuple(row) for row in spent_data]

# --- Dashboard Data ---
def fetch_summary_data(user_id, start_date, end_date):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.category_type, SUM(t.amount) as total
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ? AND t.transaction_date BETWEEN ? AND ?
        GROUP BY c.category_type
    """, (user_id, start_date, end_date))
    data = cursor.fetchall()
    conn.close()
    return [tuple(row) for row in data]