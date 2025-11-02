-- جدول الزباين
CREATE TABLE IF NOT EXISTS customers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  phone TEXT,
  notes TEXT
);

-- جدول الطلبيات
CREATE TABLE IF NOT EXISTS orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_ref TEXT,
  customer_id INTEGER,
  description TEXT,
  supplier_cost REAL DEFAULT 0,
  customs REAL DEFAULT 0,
  shipping_fee REAL DEFAULT 0,
  amount_charged REAL DEFAULT 0,
  paid_by_customer REAL DEFAULT 0,
  date TEXT,
  FOREIGN KEY(customer_id) REFERENCES customers(id)
);
