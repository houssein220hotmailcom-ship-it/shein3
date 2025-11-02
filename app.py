from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

DB = 'data.db'
app = Flask(__name__)

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with open('schema.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
    conn = get_db()
    conn.executescript(sql)
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    conn = get_db()
    cur = conn.cursor()
    total_orders = cur.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    row = cur.execute("""
        SELECT
          IFNULL(SUM(amount_charged - (supplier_cost + customs + shipping_fee)),0) as total_profit,
          IFNULL(SUM(supplier_cost + customs + shipping_fee),0) as total_capital,
          IFNULL(SUM(amount_charged),0) as total_revenue
        FROM orders
    """).fetchone()
    conn.close()
    total_profit = row['total_profit'] if row else 0
    total_capital = row['total_capital'] if row else 0
    total_revenue = row['total_revenue'] if row else 0
    return render_template('dashboard.html',
                           total_orders=total_orders,
                           total_profit=total_profit,
                           total_capital=total_capital,
                           total_revenue=total_revenue)

@app.route('/customers')
def customers():
    conn = get_db()
    cur = conn.cursor()
    rows = cur.execute("SELECT * FROM customers ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('customers.html', customers=rows)

@app.route('/customers/add', methods=['GET','POST'])
def add_customer():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form.get('phone','')
        notes = request.form.get('notes','')
        conn = get_db()
        conn.execute("INSERT INTO customers (name,phone,notes) VALUES (?,?,?)", (name,phone,notes))
        conn.commit()
        conn.close()
        return redirect(url_for('customers'))
    return render_template('add_customer.html')

@app.route('/orders')
def orders():
    conn = get_db()
    cur = conn.cursor()
    rows = cur.execute("""
      SELECT o.*, c.name as customer_name,
             (o.amount_charged - (o.supplier_cost + o.customs + o.shipping_fee)) as profit
      FROM orders o LEFT JOIN customers c ON o.customer_id = c.id
      ORDER BY o.id DESC
    """).fetchall()
    conn.close()
    return render_template('orders.html', orders=rows)

@app.route('/orders/add', methods=['GET','POST'])
def add_order():
    conn = get_db()
    cur = conn.cursor()
    customers = cur.execute("SELECT * FROM customers").fetchall()
    if request.method == 'POST':
        order_ref = request.form.get('order_ref','')
        customer_id = request.form.get('customer_id')
        description = request.form.get('description','')
        supplier_cost = float(request.form.get('supplier_cost') or 0)
        customs = float(request.form.get('customs') or 0)
        shipping_fee = float(request.form.get('shipping_fee') or 0)
        amount_charged = float(request.form.get('amount_charged') or 0)
        paid_by_customer = float(request.form.get('paid_by_customer') or 0)
        date = request.form.get('date') or datetime.utcnow().strftime('%Y-%m-%d')
        cur.execute("""INSERT INTO orders
            (order_ref, customer_id, description, supplier_cost, customs, shipping_fee, amount_charged, paid_by_customer, date)
            VALUES (?,?,?,?,?,?,?,?,?)""",
            (order_ref, customer_id, description, supplier_cost, customs, shipping_fee, amount_charged, paid_by_customer, date))
        conn.commit()
        conn.close()
        return redirect(url_for('orders'))
    conn.close()
    return render_template('add_order.html', customers=customers)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
