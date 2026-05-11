from flask import Flask, render_template, request, redirect, url_for, session, make_response
import mysql.connector
from datetime import datetime, date
from decimal import Decimal
import csv
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, HRFlowable
from reportlab.lib.units import inch

app = Flask(__name__)
app.secret_key = 'tut_secret_key_2026'

# --- 1. DATABASE CONNECTION ---
def get_db_connection():
    try:
        return mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="Njabu@08",
            database="ezasekasi_db"
        )
    except mysql.connector.Error as err:
        print(f"DATABASE ERROR: {err}")
        return None

def initialize_ai_tables():
    conn = get_db_connection()
    if conn is None:
        return
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS AI_Predictions (
                prediction_id INT AUTO_INCREMENT PRIMARY KEY,
                product_id INT NOT NULL,
                prediction_type VARCHAR(50) NOT NULL,
                prediction_value VARCHAR(100),
                confidence INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES Products(product_id) ON DELETE CASCADE
            )
        """)
        conn.commit()
    except Exception as err:
        print(f"TABLE INIT ERROR: {err}")
    finally:
        conn.close()

# --- AI INSIGHTS HELPER FUNCTIONS ---
def get_trending_products(limit=3):
    conn = get_db_connection()
    if conn is None:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.product_id, p.product_name, COALESCE(SUM(s.quantity_sold), 0) as total_sold
        FROM Products p
        LEFT JOIN Sales s ON p.product_id = s.product_id
        GROUP BY p.product_id
        ORDER BY total_sold DESC
        LIMIT %s
    """, (limit,))
    products = cursor.fetchall()
    conn.close()
    return products

def get_low_stock_warnings():
    conn = get_db_connection()
    if conn is None:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.product_id, p.product_name, p.stock_quantity, p.reorder_level,
               s.company_name as supplier_name
        FROM Products p
        LEFT JOIN Suppliers s ON p.supplier_id = s.supplier_id
        WHERE p.stock_quantity <= p.reorder_level
        ORDER BY p.stock_quantity ASC
    """)
    products = cursor.fetchall()
    conn.close()
    return products

def predict_demand_for_all_products():
    conn = get_db_connection()
    if conn is None:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.product_id, p.product_name, COALESCE(SUM(s.quantity_sold), 0) as total_sold
        FROM Products p
        LEFT JOIN Sales s ON p.product_id = s.product_id
        GROUP BY p.product_id
        ORDER BY total_sold DESC
    """)
    products = cursor.fetchall()

    # Apply demand classification rules
    for product in products:
        total_sold = product.get('total_sold', 0)
        if total_sold >= 10:
            product['demand_level'] = 'High Demand'
            product['confidence'] = 90
        elif 5 <= total_sold < 10:
            product['demand_level'] = 'Stable Demand'
            product['confidence'] = 75
        else:
            product['demand_level'] = 'Low Demand'
            product['confidence'] = 60

    conn.close()
    return products

def calculate_dynamic_credit_score(customer_id):
    conn = get_db_connection()
    if conn is None:
        return None
    cursor = conn.cursor(dictionary=True)

    # Get customer info
    cursor.execute("""
        SELECT customer_id, full_name, phone, credit_limit, current_balance
        FROM Customers WHERE customer_id = %s
    """, (customer_id,))
    customer = cursor.fetchone()

    if not customer:
        conn.close()
        return None

    # Get transaction stats
    cursor.execute("""
        SELECT COUNT(*) as total_transactions,
               SUM(CASE WHEN transaction_type = 'PAYMENT' THEN 1 ELSE 0 END) as payment_count,
               SUM(CASE WHEN transaction_type = 'SALE' THEN amount ELSE 0 END) as total_sales
        FROM Credit_Transactions
        WHERE customer_id = %s
    """, (customer_id,))
    trans = cursor.fetchone()

    conn.close()

    # Calculate score components
    total_trans = float(trans.get('total_transactions', 0) if trans else 0)
    payment_count = float(trans.get('payment_count', 0) if trans else 0)
    total_sales = float(trans.get('total_sales', 0) if trans else 0)

    # 1. Payment Reliability (40% weight)
    if total_trans > 0:
        payment_reliability = (payment_count / total_trans) * 100
    else:
        payment_reliability = 50.0

    # 2. Sales Activity (30% weight)
    if total_sales > 0:
        sales_activity = min((total_sales / 1000) * 100, 100)
    else:
        sales_activity = 0.0

    # 3. Current Status (30% weight)
    credit_limit = float(customer.get('credit_limit', 1))
    current_balance = float(customer.get('current_balance', 0))
    if credit_limit > 0:
        current_status = max(100 - (current_balance / credit_limit) * 100, 0)
    else:
        current_status = 100.0

    # Calculate final score
    final_score = (payment_reliability * 0.4) + (sales_activity * 0.3) + (current_status * 0.3)
    final_score = min(100, max(0, final_score))

    # Determine status
    if final_score >= 80:
        status_label = "Excellent"
        status_level = "excellent"
    elif final_score >= 60:
        status_label = "Good"
        status_level = "good"
    elif final_score >= 40:
        status_label = "Fair"
        status_level = "fair"
    else:
        status_label = "At Risk"
        status_level = "risk"

    return {
        'customer_id': customer_id,
        'full_name': customer.get('full_name', 'Unknown'),
        'calculated_score': round(final_score),
        'status_label': status_label,
        'status_level': status_level
    }

def get_all_credit_scores_dynamic():
    conn = get_db_connection()
    if conn is None:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT customer_id FROM Customers ORDER BY full_name")
    customers = cursor.fetchall()
    conn.close()

    scores = []
    for customer in customers:
        score = calculate_dynamic_credit_score(customer['customer_id'])
        if score:
            scores.append(score)

    return scores

def update_ai_predictions():
    products = predict_demand_for_all_products()
    conn = get_db_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()
        for product in products:
            cursor.execute("""
                INSERT INTO AI_Predictions (product_id, prediction_type, prediction_value, confidence)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                prediction_value = VALUES(prediction_value),
                confidence = VALUES(confidence),
                updated_at = CURRENT_TIMESTAMP
            """, (
                product.get('product_id'),
                'DEMAND_LEVEL',
                product.get('demand_level'),
                product.get('confidence')
            ))

        conn.commit()
    except Exception as err:
        print(f"UPDATE PREDICTIONS ERROR: {err}")
    finally:
        cursor.close()
        conn.close()

def get_products():
    conn = get_db_connection()
    if conn is None:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.*, s.company_name as supplier_name
        FROM Products p
        LEFT JOIN Suppliers s ON p.supplier_id = s.supplier_id
    """)
    products = cursor.fetchall()
    conn.close()
    return products

def get_suppliers():
    conn = get_db_connection()
    if conn is None:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT supplier_id, company_name as supplier_name, contact_person, phone, email FROM Suppliers")
    suppliers = cursor.fetchall()
    conn.close()
    return suppliers

def get_products_for_sale():
    conn = get_db_connection()
    if conn is None:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT product_id, product_name, selling_price, stock_quantity
        FROM Products
        WHERE stock_quantity > 0
        ORDER BY product_name
    """)
    products = cursor.fetchall()
    conn.close()
    return products

def get_recent_sales(limit=20):
    conn = get_db_connection()
    if conn is None:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.sale_id, p.product_name, u.full_name, s.quantity_sold,
               s.total_amount, s.sale_timestamp
        FROM Sales s
        LEFT JOIN Products p ON s.product_id = p.product_id
        LEFT JOIN Users u ON s.user_id = u.user_id
        ORDER BY s.sale_id DESC
        LIMIT %s
    """, (limit,))
    sales = cursor.fetchall()
    conn.close()
    return sales

def get_recent_stock_receipts(limit=15):
    conn = get_db_connection()
    if conn is None:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT sr.receipt_id, s.company_name as supplier_name, p.product_name,
               sr.quantity_received, u.full_name, sr.received_date
        FROM Stock_Receipts sr
        LEFT JOIN Suppliers s ON sr.supplier_id = s.supplier_id
        LEFT JOIN Products p ON sr.product_id = p.product_id
        LEFT JOIN Users u ON sr.received_by = u.user_id
        ORDER BY sr.receipt_id DESC
        LIMIT %s
    """, (limit,))
    receipts = cursor.fetchall()
    conn.close()
    return receipts

def get_customers():
    conn = get_db_connection()
    if conn is None:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT customer_id, full_name, phone, credit_limit, current_balance
        FROM Customers
        ORDER BY full_name
    """)
    customers = cursor.fetchall()
    conn.close()
    return customers

def get_customer_transactions(customer_id, limit=20):
    conn = get_db_connection()
    if conn is None:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT transaction_id, customer_id, amount, transaction_type, transaction_date
        FROM Credit_Transactions
        WHERE customer_id = %s
        ORDER BY transaction_date DESC
        LIMIT %s
    """, (customer_id, limit))
    transactions = cursor.fetchall()
    conn.close()
    return transactions

def get_recent_transactions(limit=15):
    conn = get_db_connection()
    if conn is None:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT ct.transaction_id, c.full_name, p.product_name, ct.quantity, ct.amount,
               ct.transaction_type, ct.transaction_date
        FROM Credit_Transactions ct
        LEFT JOIN Customers c ON ct.customer_id = c.customer_id
        LEFT JOIN Products p ON ct.product_id = p.product_id
        ORDER BY ct.transaction_date DESC
        LIMIT %s
    """, (limit,))
    transactions = cursor.fetchall()
    conn.close()
    return transactions

# --- PHASE 6: REPORTS HELPER FUNCTIONS ---
def get_daily_sales(report_date):
    conn = get_db_connection()
    if conn is None:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.sale_id, p.product_name, u.full_name, s.quantity_sold,
               s.total_amount, s.sale_timestamp
        FROM Sales s
        LEFT JOIN Products p ON s.product_id = p.product_id
        LEFT JOIN Users u ON s.user_id = u.user_id
        WHERE DATE(s.sale_timestamp) = %s
        ORDER BY s.sale_timestamp DESC
    """, (report_date,))
    sales = cursor.fetchall()
    conn.close()
    return sales

def get_low_stock_products(category=None):
    conn = get_db_connection()
    if conn is None:
        return []
    cursor = conn.cursor(dictionary=True)
    if category:
        cursor.execute("""
            SELECT p.product_id, p.product_name, p.category, p.stock_quantity,
                   p.reorder_level, s.company_name as supplier_name
            FROM Products p
            LEFT JOIN Suppliers s ON p.supplier_id = s.supplier_id
            WHERE p.stock_quantity <= p.reorder_level AND p.category = %s
            ORDER BY p.stock_quantity ASC
        """, (category,))
    else:
        cursor.execute("""
            SELECT p.product_id, p.product_name, p.category, p.stock_quantity,
                   p.reorder_level, s.company_name as supplier_name
            FROM Products p
            LEFT JOIN Suppliers s ON p.supplier_id = s.supplier_id
            WHERE p.stock_quantity <= p.reorder_level
            ORDER BY p.stock_quantity ASC
        """)
    products = cursor.fetchall()
    conn.close()
    return products

def get_stock_receipts_report(supplier_id=None):
    conn = get_db_connection()
    if conn is None:
        return []
    cursor = conn.cursor(dictionary=True)
    if supplier_id:
        cursor.execute("""
            SELECT sr.receipt_id, s.company_name as supplier_name, p.product_name,
                   sr.quantity_received, u.full_name, sr.received_date
            FROM Stock_Receipts sr
            LEFT JOIN Suppliers s ON sr.supplier_id = s.supplier_id
            LEFT JOIN Products p ON sr.product_id = p.product_id
            LEFT JOIN Users u ON sr.received_by = u.user_id
            WHERE sr.supplier_id = %s
            ORDER BY sr.received_date DESC
        """, (supplier_id,))
    else:
        cursor.execute("""
            SELECT sr.receipt_id, s.company_name as supplier_name, p.product_name,
                   sr.quantity_received, u.full_name, sr.received_date
            FROM Stock_Receipts sr
            LEFT JOIN Suppliers s ON sr.supplier_id = s.supplier_id
            LEFT JOIN Products p ON sr.product_id = p.product_id
            LEFT JOIN Users u ON sr.received_by = u.user_id
            ORDER BY sr.received_date DESC
        """)
    receipts = cursor.fetchall()
    conn.close()
    return receipts

def get_credit_report(customer_id=None):
    conn = get_db_connection()
    if conn is None:
        return []
    cursor = conn.cursor(dictionary=True)
    if customer_id:
        cursor.execute("""
            SELECT c.customer_id, c.full_name, c.phone, c.credit_limit, c.current_balance,
                   COUNT(ct.transaction_id) as transaction_count
            FROM Customers c
            LEFT JOIN Credit_Transactions ct ON c.customer_id = ct.customer_id
            WHERE c.customer_id = %s
            GROUP BY c.customer_id
        """, (customer_id,))
    else:
        cursor.execute("""
            SELECT c.customer_id, c.full_name, c.phone, c.credit_limit, c.current_balance,
                   COUNT(ct.transaction_id) as transaction_count
            FROM Customers c
            LEFT JOIN Credit_Transactions ct ON c.customer_id = ct.customer_id
            GROUP BY c.customer_id
            ORDER BY c.current_balance DESC
        """)
    customers = cursor.fetchall()
    conn.close()
    return customers

def get_customer_transactions_detail(customer_id):
    conn = get_db_connection()
    if conn is None:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT ct.transaction_id, p.product_name, ct.quantity, ct.amount,
               ct.transaction_type, ct.transaction_date
        FROM Credit_Transactions ct
        LEFT JOIN Products p ON ct.product_id = p.product_id
        WHERE ct.customer_id = %s
        ORDER BY ct.transaction_date DESC
    """, (customer_id,))
    transactions = cursor.fetchall()
    conn.close()
    return transactions

# --- 2. LOGIN ROUTE ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password_hash = %s", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['logged_in'] = True
            session['username'] = user['full_name']
            session['user_id'] = user['user_id']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="User not registered or incorrect credentials.")
    return render_template('login.html')

# --- 3. MAIN DASHBOARD ---
@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get all products
    cursor.execute("SELECT * FROM Products")
    products = cursor.fetchall()

    # Get credit scores
    cursor.execute("SELECT * FROM Credit_Scores")
    scores = cursor.fetchall()

    # Calculate summary statistics
    total_products = len(products)
    low_stock_products = sum(1 for p in products if p.get('stock_quantity', 0) <= p.get('reorder_level', 10))
    total_stock = sum(p.get('stock_quantity', 0) for p in products)

    # Get total sales amount
    cursor.execute("SELECT COALESCE(SUM(total_amount), 0) as total_sales FROM Sales")
    sales_result = cursor.fetchone()
    total_sales = sales_result['total_sales'] if sales_result else 0

    conn.close()

    # Get recent sales for dashboard
    recent_sales = get_recent_sales(5)

    # Get data for enhanced dashboard
    credit_customers = get_customers()
    credit_customers_count = len(credit_customers) if credit_customers else 0
    
    low_stock_warnings = get_low_stock_warnings()
    ai_alerts_count = len(low_stock_warnings) if low_stock_warnings else 0
    
    recent_stock_receipts = get_recent_stock_receipts(5) if get_recent_stock_receipts else []
    recent_credit_transactions = get_recent_transactions(5) if get_recent_transactions else []
    
    trending_products = get_trending_products(1)
    best_selling_product = trending_products[0] if trending_products else None

    return render_template('dashboard.html',
                         products=products,
                         scores=scores,
                         user=session['username'],
                         total_products=total_products,
                         low_stock_products=low_stock_products,
                         total_stock=total_stock,
                         total_sales=total_sales,
                         recent_sales=recent_sales,
                         credit_customers_count=credit_customers_count,
                         ai_alerts_count=ai_alerts_count,
                         recent_stock_receipts=recent_stock_receipts,
                         recent_credit_transactions=recent_credit_transactions,
                         low_stock_warnings=low_stock_warnings,
                         best_selling_product=best_selling_product)

# --- 4. PRODUCTS/INVENTORY PAGE - CRUD ---
@app.route('/products', methods=['GET', 'POST'])
def products():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    products_list = get_products()
    suppliers_list = get_suppliers()
    error = request.args.get('error')
    success = request.args.get('success')

    return render_template('products.html',
                         products=products_list,
                         suppliers=suppliers_list,
                         user=session['username'],
                         error=error,
                         success=success)

@app.route('/products/add', methods=['POST'])
def add_product():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        product_name = request.form.get('product_name', '').strip()
        category = request.form.get('category', '').strip()
        selling_price = request.form.get('selling_price')
        cost_price = request.form.get('cost_price')
        stock_quantity = request.form.get('stock_quantity')
        reorder_level = request.form.get('reorder_level', 10)
        expiry_date = request.form.get('expiry_date')
        supplier_id = request.form.get('supplier_id')

        # Validation
        if not product_name or len(product_name) < 2:
            return redirect(url_for('products', error='Product name must be at least 2 characters'))

        if not category:
            return redirect(url_for('products', error='Category is required'))

        try:
            selling_price = float(selling_price)
            cost_price = float(cost_price)
            stock_quantity = int(stock_quantity)
            reorder_level = int(reorder_level)
        except ValueError:
            return redirect(url_for('products', error='Invalid price or quantity values'))

        if selling_price < 0 or cost_price < 0:
            return redirect(url_for('products', error='Prices cannot be negative'))

        if stock_quantity < 0:
            return redirect(url_for('products', error='Stock cannot be negative'))

        supplier_id = supplier_id if supplier_id else None

        conn = get_db_connection()
        if conn is None:
            return redirect(url_for('products', error='Database connection failed'))

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Products
            (product_name, category, selling_price, cost_price, stock_quantity,
             reorder_level, expiry_date, supplier_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (product_name, category, selling_price, cost_price, stock_quantity,
              reorder_level, expiry_date if expiry_date else None, supplier_id))

        conn.commit()
        conn.close()
        return redirect(url_for('products', success='Product added successfully'))

    except Exception as err:
        print(f"ADD PRODUCT ERROR: {err}")
        return redirect(url_for('products', error='Failed to add product'))

@app.route('/products/update/<int:product_id>', methods=['POST'])
def update_product(product_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        product_name = request.form.get('product_name', '').strip()
        category = request.form.get('category', '').strip()
        selling_price = request.form.get('selling_price')
        cost_price = request.form.get('cost_price')
        stock_quantity = request.form.get('stock_quantity')
        reorder_level = request.form.get('reorder_level', 10)
        expiry_date = request.form.get('expiry_date')
        supplier_id = request.form.get('supplier_id')

        # Validation
        if not product_name or len(product_name) < 2:
            return redirect(url_for('products', error='Product name must be at least 2 characters'))

        if not category:
            return redirect(url_for('products', error='Category is required'))

        try:
            selling_price = float(selling_price)
            cost_price = float(cost_price)
            stock_quantity = int(stock_quantity)
            reorder_level = int(reorder_level)
        except ValueError:
            return redirect(url_for('products', error='Invalid price or quantity values'))

        if selling_price < 0 or cost_price < 0:
            return redirect(url_for('products', error='Prices cannot be negative'))

        if stock_quantity < 0:
            return redirect(url_for('products', error='Stock cannot be negative'))

        supplier_id = supplier_id if supplier_id else None

        conn = get_db_connection()
        if conn is None:
            return redirect(url_for('products', error='Database connection failed'))

        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Products
            SET product_name=%s, category=%s, selling_price=%s, cost_price=%s,
                stock_quantity=%s, reorder_level=%s, expiry_date=%s, supplier_id=%s
            WHERE product_id=%s
        """, (product_name, category, selling_price, cost_price, stock_quantity,
              reorder_level, expiry_date if expiry_date else None, supplier_id, product_id))

        conn.commit()
        conn.close()
        return redirect(url_for('products', success='Product updated successfully'))

    except Exception as err:
        print(f"UPDATE PRODUCT ERROR: {err}")
        return redirect(url_for('products', error='Failed to update product'))

@app.route('/products/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        conn = get_db_connection()
        if conn is None:
            return redirect(url_for('products', error='Database connection failed'))

        cursor = conn.cursor()
        cursor.execute("DELETE FROM Products WHERE product_id=%s", (product_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('products', success='Product deleted successfully'))

    except Exception as err:
        print(f"DELETE PRODUCT ERROR: {err}")
        return redirect(url_for('products', error='Failed to delete product'))

# --- 5. SALES/POS PAGE ---
@app.route('/sales', methods=['GET', 'POST'])
def sales():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Always get fresh data from database
    products_list = get_products_for_sale()
    sales_list = get_recent_sales(20)
    error = request.args.get('error')
    success = request.args.get('success')

    return render_template('sales.html',
                         products=products_list,
                         sales=sales_list,
                         user=session['username'],
                         error=error,
                         success=success)

@app.route('/sales/add', methods=['POST'])
def add_sale():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity')

        # Validation
        if not product_id or not quantity:
            return redirect(url_for('sales', error='Please select product and enter quantity'))

        try:
            product_id = int(product_id)
            quantity = int(quantity)
        except ValueError:
            return redirect(url_for('sales', error='Invalid product or quantity'))

        if quantity <= 0:
            return redirect(url_for('sales', error='Quantity must be greater than 0'))

        user_id = session.get('user_id')

        conn = get_db_connection()
        if conn is None:
            return redirect(url_for('sales', error='Database connection failed'))

        cursor = conn.cursor(dictionary=True)

        # Check if product exists and has enough stock
        cursor.execute("SELECT stock_quantity, selling_price FROM Products WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()

        if not product:
            conn.close()
            return redirect(url_for('sales', error='Product not found'))

        if product['stock_quantity'] < quantity:
            conn.close()
            return redirect(url_for('sales', error=f'Insufficient stock. Available: {product["stock_quantity"]}'))

        # Calculate total amount
        total_amount = quantity * product['selling_price']

        # Insert sale
        cursor.execute("""
            INSERT INTO Sales (product_id, user_id, quantity_sold, total_amount)
            VALUES (%s, %s, %s, %s)
        """, (product_id, user_id, quantity, total_amount))

        # Update product stock
        cursor.execute("""
            UPDATE Products SET stock_quantity = stock_quantity - %s
            WHERE product_id = %s
        """, (quantity, product_id))

        conn.commit()
        conn.close()

        return redirect(url_for('sales', success=f'Sale recorded successfully: R{total_amount:.2f}'))

    except Exception as err:
        print(f"ADD SALE ERROR: {err}")
        return redirect(url_for('sales', error=f'Failed to record sale: {str(err)}'))

# --- 6. SUPPLIERS PAGE ---
@app.route('/suppliers', methods=['GET', 'POST'])
def suppliers():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    suppliers_list = get_suppliers()
    products_list = get_products_for_sale()
    receipts_list = get_recent_stock_receipts(15)
    error = request.args.get('error')
    success = request.args.get('success')

    return render_template('suppliers.html',
                         suppliers=suppliers_list,
                         products=products_list,
                         receipts=receipts_list,
                         user=session['username'],
                         error=error,
                         success=success)

@app.route('/suppliers/add', methods=['POST'])
def add_supplier():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        company_name = request.form.get('company_name', '').strip()
        contact_person = request.form.get('contact_person', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()

        if not company_name or len(company_name) < 2:
            return redirect(url_for('suppliers', error='Company name must be at least 2 characters'))

        conn = get_db_connection()
        if conn is None:
            return redirect(url_for('suppliers', error='Database connection failed'))

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Suppliers (company_name, contact_person, phone, email)
            VALUES (%s, %s, %s, %s)
        """, (company_name, contact_person if contact_person else None,
              phone if phone else None, email if email else None))

        conn.commit()
        conn.close()
        return redirect(url_for('suppliers', success='Supplier added successfully'))

    except Exception as err:
        print(f"ADD SUPPLIER ERROR: {err}")
        return redirect(url_for('suppliers', error='Failed to add supplier'))

@app.route('/suppliers/update/<int:supplier_id>', methods=['POST'])
def update_supplier(supplier_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        company_name = request.form.get('company_name', '').strip()
        contact_person = request.form.get('contact_person', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()

        if not company_name or len(company_name) < 2:
            return redirect(url_for('suppliers', error='Company name must be at least 2 characters'))

        conn = get_db_connection()
        if conn is None:
            return redirect(url_for('suppliers', error='Database connection failed'))

        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Suppliers
            SET company_name=%s, contact_person=%s, phone=%s, email=%s
            WHERE supplier_id=%s
        """, (company_name, contact_person if contact_person else None,
              phone if phone else None, email if email else None, supplier_id))

        conn.commit()
        conn.close()
        return redirect(url_for('suppliers', success='Supplier updated successfully'))

    except Exception as err:
        print(f"UPDATE SUPPLIER ERROR: {err}")
        return redirect(url_for('suppliers', error='Failed to update supplier'))

@app.route('/suppliers/delete/<int:supplier_id>', methods=['POST'])
def delete_supplier(supplier_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        conn = get_db_connection()
        if conn is None:
            return redirect(url_for('suppliers', error='Database connection failed'))

        cursor = conn.cursor()
        cursor.execute("DELETE FROM Suppliers WHERE supplier_id=%s", (supplier_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('suppliers', success='Supplier deleted successfully'))

    except Exception as err:
        print(f"DELETE SUPPLIER ERROR: {err}")
        return redirect(url_for('suppliers', error='Failed to delete supplier'))

@app.route('/suppliers/receive', methods=['POST'])
def receive_stock():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        supplier_id = request.form.get('supplier_id')
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity')

        if not supplier_id or not product_id or not quantity:
            return redirect(url_for('suppliers', error='Please select supplier, product and enter quantity'))

        try:
            supplier_id = int(supplier_id)
            product_id = int(product_id)
            quantity = int(quantity)
        except ValueError:
            return redirect(url_for('suppliers', error='Invalid supplier, product or quantity'))

        if quantity <= 0:
            return redirect(url_for('suppliers', error='Quantity must be greater than 0'))

        user_id = session.get('user_id')

        conn = get_db_connection()
        if conn is None:
            return redirect(url_for('suppliers', error='Database connection failed'))

        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT product_id FROM Products WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()

        if not product:
            conn.close()
            return redirect(url_for('suppliers', error='Product not found'))

        cursor.execute("""
            INSERT INTO Stock_Receipts (supplier_id, product_id, quantity_received, received_by)
            VALUES (%s, %s, %s, %s)
        """, (supplier_id, product_id, quantity, user_id))

        cursor.execute("""
            UPDATE Products SET stock_quantity = stock_quantity + %s
            WHERE product_id = %s
        """, (quantity, product_id))

        conn.commit()
        conn.close()

        return redirect(url_for('suppliers', success=f'Stock received: +{quantity} units'))

    except Exception as err:
        print(f"RECEIVE STOCK ERROR: {err}")
        return redirect(url_for('suppliers', error=f'Failed to receive stock: {str(err)}'))

# --- 7. CREDIT CUSTOMERS PAGE ---
@app.route('/credit-customers', methods=['GET', 'POST'])
def credit_customers():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    customers_list = get_customers()
    products_list = get_products_for_sale()
    transactions_list = get_recent_transactions(15)
    error = request.args.get('error')
    success = request.args.get('success')

    return render_template('credit_customers.html',
                         customers=customers_list,
                         products=products_list,
                         transactions=transactions_list,
                         user=session['username'],
                         error=error,
                         success=success)

@app.route('/credit-customers/add', methods=['POST'])
def add_customer():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        credit_limit = request.form.get('credit_limit')

        if not full_name or len(full_name) < 2:
            return redirect(url_for('credit_customers', error='Name must be at least 2 characters'))

        try:
            credit_limit = float(credit_limit)
        except (ValueError, TypeError):
            return redirect(url_for('credit_customers', error='Invalid credit limit'))

        if credit_limit < 0:
            return redirect(url_for('credit_customers', error='Credit limit cannot be negative'))

        conn = get_db_connection()
        if conn is None:
            return redirect(url_for('credit_customers', error='Database connection failed'))

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Customers (full_name, phone, credit_limit, current_balance)
            VALUES (%s, %s, %s, 0)
        """, (full_name, phone if phone else None, credit_limit))

        conn.commit()
        conn.close()
        return redirect(url_for('credit_customers', success='Customer added successfully'))

    except Exception as err:
        print(f"ADD CUSTOMER ERROR: {err}")
        return redirect(url_for('credit_customers', error='Failed to add customer'))

@app.route('/credit-customers/update/<int:customer_id>', methods=['POST'])
def update_customer(customer_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        credit_limit = request.form.get('credit_limit')

        if not full_name or len(full_name) < 2:
            return redirect(url_for('credit_customers', error='Name must be at least 2 characters'))

        try:
            credit_limit = float(credit_limit)
        except (ValueError, TypeError):
            return redirect(url_for('credit_customers', error='Invalid credit limit'))

        if credit_limit < 0:
            return redirect(url_for('credit_customers', error='Credit limit cannot be negative'))

        conn = get_db_connection()
        if conn is None:
            return redirect(url_for('credit_customers', error='Database connection failed'))

        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Customers
            SET full_name=%s, phone=%s, credit_limit=%s
            WHERE customer_id=%s
        """, (full_name, phone if phone else None, credit_limit, customer_id))

        conn.commit()
        conn.close()
        return redirect(url_for('credit_customers', success='Customer updated successfully'))

    except Exception as err:
        print(f"UPDATE CUSTOMER ERROR: {err}")
        return redirect(url_for('credit_customers', error='Failed to update customer'))

@app.route('/credit-customers/delete/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        conn = get_db_connection()
        if conn is None:
            return redirect(url_for('credit_customers', error='Database connection failed'))

        cursor = conn.cursor()
        cursor.execute("DELETE FROM Customers WHERE customer_id=%s", (customer_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('credit_customers', success='Customer deleted successfully'))

    except Exception as err:
        print(f"DELETE CUSTOMER ERROR: {err}")
        return redirect(url_for('credit_customers', error='Failed to delete customer'))

@app.route('/credit-customers/credit-sale', methods=['POST'])
def record_credit_sale():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        customer_id = request.form.get('customer_id')
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity')

        if not customer_id or not product_id or not quantity:
            return redirect(url_for('credit_customers', error='Please select customer, product and enter quantity'))

        try:
            customer_id = int(customer_id)
            product_id = int(product_id)
            quantity = int(quantity)
        except (ValueError, TypeError):
            return redirect(url_for('credit_customers', error='Invalid customer, product or quantity'))

        if quantity <= 0:
            return redirect(url_for('credit_customers', error='Quantity must be greater than 0'))

        conn = get_db_connection()
        if conn is None:
            return redirect(url_for('credit_customers', error='Database connection failed'))

        cursor = conn.cursor(dictionary=True)

        # Get customer info
        cursor.execute("""
            SELECT customer_id, credit_limit, current_balance
            FROM Customers WHERE customer_id = %s
        """, (customer_id,))
        customer = cursor.fetchone()

        if not customer:
            conn.close()
            return redirect(url_for('credit_customers', error='Customer not found'))

        # Get product info
        cursor.execute("""
            SELECT product_id, product_name, selling_price, stock_quantity
            FROM Products WHERE product_id = %s
        """, (product_id,))
        product = cursor.fetchone()

        if not product:
            conn.close()
            return redirect(url_for('credit_customers', error='Product not found'))

        # Check stock
        if product['stock_quantity'] < quantity:
            conn.close()
            return redirect(url_for('credit_customers', error=f'Insufficient stock. Available: {product["stock_quantity"]} units'))

        # Calculate sale amount
        amount = Decimal(str(quantity)) * Decimal(str(product['selling_price']))
        new_balance = customer['current_balance'] + amount

        # Check credit limit
        if new_balance > customer['credit_limit']:
            conn.close()
            return redirect(url_for('credit_customers', error=f'Credit limit exceeded. Limit: R{customer["credit_limit"]:.2f}, New balance would be: R{new_balance:.2f}'))

        # Record transaction
        cursor.execute("""
            INSERT INTO Credit_Transactions (customer_id, product_id, quantity, amount, transaction_type)
            VALUES (%s, %s, %s, %s, 'SALE')
        """, (customer_id, product_id, quantity, amount))

        # Update customer balance
        cursor.execute("""
            UPDATE Customers SET current_balance = current_balance + %s
            WHERE customer_id = %s
        """, (amount, customer_id))

        # Update product stock
        cursor.execute("""
            UPDATE Products SET stock_quantity = stock_quantity - %s
            WHERE product_id = %s
        """, (quantity, product_id))

        conn.commit()
        conn.close()

        return redirect(url_for('credit_customers', success=f'Credit sale recorded: {quantity}x {product["product_name"]} = R{amount:.2f}'))

    except Exception as err:
        print(f"CREDIT SALE ERROR: {err}")
        return redirect(url_for('credit_customers', error=f'Failed to record sale: {str(err)}'))

@app.route('/credit-customers/payment', methods=['POST'])
def record_payment():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        customer_id = request.form.get('customer_id')
        amount = request.form.get('amount')

        if not customer_id or not amount:
            return redirect(url_for('credit_customers', error='Please select customer and enter amount'))

        try:
            customer_id = int(customer_id)
            amount = Decimal(str(amount))
        except (ValueError, TypeError):
            return redirect(url_for('credit_customers', error='Invalid customer or amount'))

        if amount <= 0:
            return redirect(url_for('credit_customers', error='Amount must be greater than 0'))

        conn = get_db_connection()
        if conn is None:
            return redirect(url_for('credit_customers', error='Database connection failed'))

        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT customer_id, current_balance
            FROM Customers WHERE customer_id = %s
        """, (customer_id,))
        customer = cursor.fetchone()

        if not customer:
            conn.close()
            return redirect(url_for('credit_customers', error='Customer not found'))

        new_balance = customer['current_balance'] - amount

        if new_balance < 0:
            conn.close()
            return redirect(url_for('credit_customers', error=f'Payment exceeds outstanding balance. Current balance: R{customer["current_balance"]:.2f}'))

        cursor.execute("""
            INSERT INTO Credit_Transactions (customer_id, amount, transaction_type)
            VALUES (%s, %s, 'PAYMENT')
        """, (customer_id, amount))

        cursor.execute("""
            UPDATE Customers SET current_balance = current_balance - %s
            WHERE customer_id = %s
        """, (amount, customer_id))

        conn.commit()
        conn.close()

        return redirect(url_for('credit_customers', success=f'Payment recorded: R{amount:.2f}'))

    except Exception as err:
        print(f"PAYMENT ERROR: {err}")
        return redirect(url_for('credit_customers', error=f'Failed to record payment: {str(err)}'))

# --- 8. REPORTS PAGE ---
@app.route('/reports')
def reports():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    today = date.today().strftime('%Y-%m-%d')
    suppliers_list = get_suppliers()
    customers_list = get_customers()
    categories = ['Dairy', 'Bakery', 'Pantry', 'Beverage', 'Snacks', 'Toiletries', 'Cleaning', 'Other']

    # Get report data
    daily_sales = get_daily_sales(today)
    low_stock = get_low_stock_products()
    stock_receipts = get_stock_receipts_report()
    credit_report = get_credit_report()
    total_outstanding = sum(Decimal(str(c.get('current_balance', 0))) for c in credit_report)

    return render_template('reports.html',
                         user=session['username'],
                         daily_sales=daily_sales,
                         low_stock=low_stock,
                         stock_receipts=stock_receipts,
                         credit_report=credit_report,
                         total_outstanding=total_outstanding,
                         suppliers=suppliers_list,
                         customers=customers_list,
                         categories=categories,
                         today=today)

@app.route('/reports/daily-sales')
def report_daily_sales():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    report_date = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    suppliers_list = get_suppliers()
    customers_list = get_customers()
    categories = ['Dairy', 'Bakery', 'Pantry', 'Beverage', 'Snacks', 'Toiletries', 'Cleaning', 'Other']

    daily_sales = get_daily_sales(report_date)
    low_stock = get_low_stock_products()
    stock_receipts = get_stock_receipts_report()
    credit_report = get_credit_report()
    total_outstanding = sum(Decimal(str(c.get('current_balance', 0))) for c in credit_report)

    return render_template('reports.html',
                         user=session['username'],
                         daily_sales=daily_sales,
                         low_stock=low_stock,
                         stock_receipts=stock_receipts,
                         credit_report=credit_report,
                         total_outstanding=total_outstanding,
                         suppliers=suppliers_list,
                         customers=customers_list,
                         categories=categories,
                         today=date.today().strftime('%Y-%m-%d'),
                         report_date=report_date,
                         active_tab='sales')

@app.route('/reports/low-stock')
def report_low_stock():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    category = request.args.get('category', '')
    suppliers_list = get_suppliers()
    customers_list = get_customers()
    categories = ['Dairy', 'Bakery', 'Pantry', 'Beverage', 'Snacks', 'Toiletries', 'Cleaning', 'Other']

    if category:
        low_stock = get_low_stock_products(category)
    else:
        low_stock = get_low_stock_products()

    daily_sales = get_daily_sales(date.today().strftime('%Y-%m-%d'))
    stock_receipts = get_stock_receipts_report()
    credit_report = get_credit_report()
    total_outstanding = sum(Decimal(str(c.get('current_balance', 0))) for c in credit_report)

    return render_template('reports.html',
                         user=session['username'],
                         daily_sales=daily_sales,
                         low_stock=low_stock,
                         stock_receipts=stock_receipts,
                         credit_report=credit_report,
                         total_outstanding=total_outstanding,
                         suppliers=suppliers_list,
                         customers=customers_list,
                         categories=categories,
                         today=date.today().strftime('%Y-%m-%d'),
                         selected_category=category,
                         active_tab='stock')

@app.route('/reports/stock-receipts')
def report_stock_receipts():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    supplier_id = request.args.get('supplier_id', '')
    suppliers_list = get_suppliers()
    customers_list = get_customers()
    categories = ['Dairy', 'Bakery', 'Pantry', 'Beverage', 'Snacks', 'Toiletries', 'Cleaning', 'Other']

    if supplier_id:
        stock_receipts = get_stock_receipts_report(supplier_id)
    else:
        stock_receipts = get_stock_receipts_report()

    daily_sales = get_daily_sales(date.today().strftime('%Y-%m-%d'))
    low_stock = get_low_stock_products()
    credit_report = get_credit_report()
    total_outstanding = sum(Decimal(str(c.get('current_balance', 0))) for c in credit_report)

    return render_template('reports.html',
                         user=session['username'],
                         daily_sales=daily_sales,
                         low_stock=low_stock,
                         stock_receipts=stock_receipts,
                         credit_report=credit_report,
                         total_outstanding=total_outstanding,
                         suppliers=suppliers_list,
                         customers=customers_list,
                         categories=categories,
                         today=date.today().strftime('%Y-%m-%d'),
                         selected_supplier=supplier_id,
                         active_tab='receipts')

@app.route('/reports/credit-balances')
def report_credit_balances():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    customer_id = request.args.get('customer_id', '')
    suppliers_list = get_suppliers()
    customers_list = get_customers()
    categories = ['Dairy', 'Bakery', 'Pantry', 'Beverage', 'Snacks', 'Toiletries', 'Cleaning', 'Other']

    if customer_id:
        credit_report = get_credit_report(customer_id)
    else:
        credit_report = get_credit_report()

    total_outstanding = sum(Decimal(str(c.get('current_balance', 0))) for c in credit_report)

    daily_sales = get_daily_sales(date.today().strftime('%Y-%m-%d'))
    low_stock = get_low_stock_products()
    stock_receipts = get_stock_receipts_report()

    return render_template('reports.html',
                         user=session['username'],
                         daily_sales=daily_sales,
                         low_stock=low_stock,
                         stock_receipts=stock_receipts,
                         credit_report=credit_report,
                         total_outstanding=total_outstanding,
                         suppliers=suppliers_list,
                         customers=customers_list,
                         categories=categories,
                         today=date.today().strftime('%Y-%m-%d'),
                         selected_customer=customer_id,
                         active_tab='credit')

@app.route('/reports/export-sales')
def export_sales():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Get date from query params, with validation
    report_date = request.args.get('date', '').strip()
    if not report_date:
        report_date = date.today().strftime('%Y-%m-%d')
    
    # Validate date format
    try:
        from datetime import datetime
        datetime.strptime(report_date, '%Y-%m-%d')
    except ValueError:
        return redirect(url_for('reports', error='Invalid date format. Please use YYYY-MM-DD'))
    
    daily_sales = get_daily_sales(report_date)

    # Create CSV with proper encoding
    output = io.StringIO()
    writer = csv.writer(output, lineterminator='\n')

    # Header section
    writer.writerow(['EZASEKASI SPAZA SHOP - Daily Sales Report'])
    writer.writerow(['Date: ' + report_date])
    writer.writerow([])

    # Column headers
    writer.writerow(['Sale ID', 'Product', 'Cashier', 'Quantity', 'Total Amount', 'Timestamp'])

    total_sales = 0
    for sale in daily_sales:
        amount = float(sale['total_amount'] or 0)
        writer.writerow([
            sale['sale_id'],
            sale['product_name'] or 'Unknown',
            sale['full_name'] or 'Unknown',
            sale['quantity_sold'],
            f"{amount:.2f}",
            sale['sale_timestamp'].strftime('%Y-%m-%d %H:%M:%S') if sale['sale_timestamp'] else ''
        ])
        total_sales += amount

    # Summary
    writer.writerow([])
    writer.writerow(['TOTAL SALES', '', '', '', f'{total_sales:.2f}', ''])

    # Convert to bytes with UTF-8 encoding
    csv_content = output.getvalue().encode('utf-8-sig')

    response = make_response(csv_content)
    response.headers['Content-Disposition'] = f'attachment; filename=sales_report_{report_date}.csv'
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Length'] = len(csv_content)

    return response

@app.route('/reports/export-sales-pdf')
def export_sales_pdf():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Get date from query params, with validation
    report_date = request.args.get('date', '').strip()
    if not report_date:
        report_date = date.today().strftime('%Y-%m-%d')
    
    # Validate date format
    try:
        from datetime import datetime as dt
        dt.strptime(report_date, '%Y-%m-%d')
        report_datetime = dt.now()
    except ValueError:
        return redirect(url_for('reports', error='Invalid date format. Please use YYYY-MM-DD'))
    
    daily_sales = get_daily_sales(report_date)

    # Create PDF
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)

    elements = []
    styles = getSampleStyleSheet()

    # ===== REPORT HEADER =====
    header_style = ParagraphStyle(
        'ReportHeader',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#0054a6'),
        spaceAfter=3,
        alignment=1,
        fontName='Helvetica-Bold'
    )
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#666666'),
        spaceAfter=2,
        alignment=1
    )
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#333333'),
        spaceAfter=1
    )

    # Header content
    elements.append(Paragraph('📊 EZASEKASI SPAZA SHOP', header_style))
    elements.append(Paragraph('Daily Sales Report', ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#ed1c24'),
        spaceAfter=6,
        alignment=1
    )))
    
    # Report metadata
    elements.append(Paragraph(f'Report Date: {report_date}', info_style))
    elements.append(Paragraph(f'Generated: {report_datetime.strftime("%d %B %Y at %H:%M:%S")}', info_style))
    elements.append(Paragraph('Report Type: Daily Sales Analysis', info_style))
    elements.append(Spacer(1, 0.2*inch))

    # Horizontal line
    line = HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0054a6'))
    elements.append(line)
    elements.append(Spacer(1, 0.2*inch))

    # ===== HANDLE NO SALES DATA =====
    if not daily_sales:
        no_sales_style = ParagraphStyle(
            'NoSales',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#ed1c24'),
            alignment=1,
            spaceAfter=12
        )
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph('📭 No Sales Data Available', no_sales_style))
        elements.append(Paragraph('There were no sales recorded on this date.', styles['Normal']))
        elements.append(Spacer(1, 0.5*inch))
        
        # Build and return
        doc.build(elements)
        pdf_buffer.seek(0)
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename=sales_report_{report_date}.pdf'
        response.headers['Content-Type'] = 'application/pdf'
        return response

    # ===== SALES SUMMARY SECTION =====
    summary_data = {
        'total_sales': 0,
        'total_quantity': 0,
        'transaction_count': len(daily_sales),
        'products_sold': {}
    }

    for sale in daily_sales:
        amount = float(sale['total_amount'] or 0)
        quantity = int(sale['quantity_sold'] or 0)
        product = sale['product_name'] or 'Unknown'
        
        summary_data['total_sales'] += amount
        summary_data['total_quantity'] += quantity
        
        if product not in summary_data['products_sold']:
            summary_data['products_sold'][product] = {'qty': 0, 'amount': 0}
        summary_data['products_sold'][product]['qty'] += quantity
        summary_data['products_sold'][product]['amount'] += amount

    avg_sale = summary_data['total_sales'] / summary_data['transaction_count'] if summary_data['transaction_count'] > 0 else 0
    best_product = max(summary_data['products_sold'].items(), key=lambda x: x[1]['qty'])[0] if summary_data['products_sold'] else 'N/A'

    # Summary cards in grid format
    summary_title = ParagraphStyle(
        'SummaryTitle',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.HexColor('#0054a6'),
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )
    elements.append(Paragraph('📊 Sales Summary', summary_title))

    summary_table_data = [
        ['Total Sales', f"R{summary_data['total_sales']:.2f}"],
        ['Total Transactions', str(summary_data['transaction_count'])],
        ['Total Units Sold', str(summary_data['total_quantity'])],
        ['Average Sale Amount', f"R{avg_sale:.2f}"],
        ['Best-Selling Product', best_product]
    ]

    summary_table = Table(summary_table_data, colWidths=[2.5*inch, 2.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#ffffff')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0054a6')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 0.25*inch))

    # ===== DETAILED SALES TABLE =====
    table_title = ParagraphStyle(
        'TableTitle',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.HexColor('#0054a6'),
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )
    elements.append(Paragraph('📋 Detailed Sales Transactions', table_title))

    table_data = [['Sale ID', 'Product', 'Quantity', 'Price', 'Total Amount', 'Cashier', 'Time']]

    for sale in daily_sales:
        amount = float(sale['total_amount'] or 0)
        quantity = int(sale['quantity_sold'] or 0)
        unit_price = amount / quantity if quantity > 0 else 0
        
        table_data.append([
            str(sale['sale_id']),
            sale['product_name'] or 'Unknown',
            str(quantity),
            f"R{unit_price:.2f}",
            f"R{amount:.2f}",
            sale['full_name'] or 'Unknown',
            sale['sale_timestamp'].strftime('%H:%M:%S') if sale['sale_timestamp'] else 'N/A'
        ])

    # Add total row
    table_data.append(['', '', '', 'TOTAL', f"R{summary_data['total_sales']:.2f}", '', ''])

    table = Table(table_data, colWidths=[0.7*inch, 1.8*inch, 0.65*inch, 0.65*inch, 1*inch, 1.3*inch, 0.75*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0054a6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ffcc00')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f9f9f9')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.2*inch))

    # ===== LOW STOCK WARNING SECTION =====
    low_stock_products = get_low_stock_warnings()
    if low_stock_products:
        warning_title = ParagraphStyle(
            'WarningTitle',
            parent=styles['Heading2'],
            fontSize=13,
            textColor=colors.HexColor('#ed1c24'),
            spaceAfter=8,
            fontName='Helvetica-Bold'
        )
        elements.append(Paragraph('⚠️ Low Stock Alert', warning_title))

        warning_data = [['Product', 'Current Stock', 'Reorder Level', 'Shortage', 'Supplier']]
        for product in low_stock_products[:10]:  # Show top 10
            shortage = product['reorder_level'] - product['stock_quantity']
            warning_data.append([
                product['product_name'],
                str(product['stock_quantity']),
                str(product['reorder_level']),
                str(shortage),
                product['supplier_name'] or 'N/A'
            ])

        warning_table = Table(warning_data, colWidths=[1.8*inch, 1.2*inch, 1.2*inch, 1*inch, 1.5*inch])
        warning_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ed1c24')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ffcccc')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff5f5')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        elements.append(warning_table)
        elements.append(Spacer(1, 0.2*inch))

    # ===== AI INSIGHTS SECTION =====
    trending = get_trending_products(3)
    if trending:
        ai_title = ParagraphStyle(
            'AITitle',
            parent=styles['Heading2'],
            fontSize=13,
            textColor=colors.HexColor('#0054a6'),
            spaceAfter=8,
            fontName='Helvetica-Bold'
        )
        elements.append(Paragraph('🤖 AI Insights & Recommendations', ai_title))

        # Top selling products
        ai_data = [['🏆 Top Performing Products', 'Units Sold']]
        for trend in trending:
            ai_data.append([
                trend['product_name'],
                str(trend['total_sold'])
            ])

        ai_table = Table(ai_data, colWidths=[3.5*inch, 1.5*inch])
        ai_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ffcc00')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0054a6')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#f0d000')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fffef0')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(ai_table)
        elements.append(Spacer(1, 0.15*inch))

        # Recommendations
        rec_style = ParagraphStyle(
            'RecStyle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#333333'),
            spaceAfter=4
        )
        elements.append(Paragraph('💡 <b>Recommendations:</b>', rec_style))
        if summary_data['total_sales'] > 1000:
            elements.append(Paragraph('✓ Strong sales performance. Consider increasing stock for best-selling products.', rec_style))
        if len(low_stock_products) > 0:
            elements.append(Paragraph(f'✓ {len(low_stock_products)} products below reorder level. Schedule urgent restocking.', rec_style))
        elements.append(Paragraph(f'✓ Average sale value is R{avg_sale:.2f}. Monitor pricing and promotions accordingly.', rec_style))

    # ===== FOOTER =====
    elements.append(Spacer(1, 0.3*inch))
    footer_line = HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc'))
    elements.append(footer_line)
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#999999'),
        alignment=1
    )
    elements.append(Paragraph('This report was automatically generated by Ezasekasi Spaza Shop System', footer_style))
    elements.append(Paragraph(f'Confidential - For Internal Use Only • Report ID: SR-{report_date.replace("-", "")}', footer_style))

    # Build PDF
    doc.build(elements)
    pdf_buffer.seek(0)

    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=sales_report_{report_date}.pdf'
    response.headers['Content-Type'] = 'application/pdf'

    return response

# --- 9. LOGOUT ROUTE ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- 10. DATA ACTIONS (PERSISTENCE LOGIC) ---
@app.route('/update/<int:id>', methods=['POST'])
def update_stock(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        new_stock = int(request.form['stock'])

        if new_stock < 0:
            products = get_products()
            return render_template('dashboard.html',
                                   error="Stock cannot be negative!",
                                   products=products,
                                   user=session['username'])

        conn = get_db_connection()
        if conn is None:
            products = get_products()
            return render_template('dashboard.html',
                                   error="Database connection failed!",
                                   products=products,
                                   user=session['username'])

        cursor = conn.cursor()
        cursor.execute("UPDATE Products SET stock_quantity = %s WHERE product_id = %s", (new_stock, id))
        conn.commit()
        conn.close()

    except ValueError:
        products = get_products()
        return render_template('dashboard.html',
                               error="Invalid stock value!",
                               products=products,
                               user=session['username'])
    except Exception as err:
        print(f"UPDATE ERROR: {err}")
        products = get_products()
        return render_template('dashboard.html',
                               error="Update failed!",
                               products=products,
                               user=session['username'])

    return redirect(url_for('index'))

@app.route('/sell/<int:id>', methods=['POST'])
def sell_item(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Products SET stock_quantity = stock_quantity - 1 WHERE product_id = %s AND stock_quantity > 0", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
