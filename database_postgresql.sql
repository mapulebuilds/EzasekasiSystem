DROP TABLE IF EXISTS credit_transactions CASCADE;
DROP TABLE IF EXISTS stock_receipts CASCADE;
DROP TABLE IF EXISTS sales CASCADE;
DROP TABLE IF EXISTS ai_predictions CASCADE;
DROP TABLE IF EXISTS credit_scores CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS suppliers CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
  user_id SERIAL PRIMARY KEY,
  full_name VARCHAR(100) NOT NULL,
  user_role VARCHAR(10) NOT NULL CHECK (user_role IN ('Owner','Cashier','Supplier','Admin')),
  username VARCHAR(50) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  contact_number VARCHAR(15)
);

INSERT INTO users (user_id, full_name, user_role, username, password_hash, contact_number) VALUES
(1,'Mercy Molonyama','Owner','mercy_m','123456',NULL),
(2,'Happiness Simao','Admin','happy_s','123456',NULL),
(3,'Brightness Masilela','Cashier','bri_m','123456',NULL),
(4,'Kearabetswe Lebelo','Cashier','kea_l','123456',NULL),
(5,'Karabo Komane','Supplier','kaybee_k','123456',NULL),
(6,'Tau Thamaga','Cashier','tau_t','123456',NULL),
(7,'Percy Thotse','Cashier','percy_t','123456',NULL),
(8,'Tshwarelo Mahlako','Admin','tshwarelo_m','123456',NULL),
(9,'Samkelisiwe Mngadi','Cashier','samke_m','123456',NULL);

SELECT setval('users_user_id_seq', 9);

CREATE TABLE suppliers (
  supplier_id SERIAL PRIMARY KEY,
  company_name VARCHAR(100) NOT NULL,
  contact_person VARCHAR(100),
  phone VARCHAR(15),
  email VARCHAR(100)
);

INSERT INTO suppliers (supplier_id, company_name, contact_person, phone, email) VALUES
(1,'Tshwane Wholesalers','Mr. Dube','0125550001',NULL),
(2,'Emalahleni Bakery','Sarah','0135559999',NULL),
(3,'Beverage Corp','John','0114441111',NULL),
(4,'Dairy Fresh','Lerato','0127778888',NULL),
(5,'Agri-Nathi Logistics','Thabo','0153332222',NULL);

SELECT setval('suppliers_supplier_id_seq', 5);

CREATE TABLE products (
  product_id SERIAL PRIMARY KEY,
  product_name VARCHAR(100) NOT NULL,
  category VARCHAR(50),
  cost_price DECIMAL(10,2),
  selling_price DECIMAL(10,2) NOT NULL,
  stock_quantity INT DEFAULT 0,
  reorder_level INT DEFAULT 5,
  expiry_date DATE,
  supplier_id INT,
  FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

INSERT INTO products (product_id, product_name, category, cost_price, selling_price, stock_quantity, reorder_level, expiry_date, supplier_id) VALUES
(1,'Milk 2L','Dairy',24.50,35.00,20,5,'2026-12-31',4),
(2,'Brown Bread','Bakery',12.00,18.50,15,5,'2026-06-30',2),
(3,'Sugar 2kg','Pantry',35.00,48.00,3,5,'2027-01-31',1),
(4,'Coke 500ml','Beverage',10.00,15.00,48,10,'2026-11-30',3),
(5,'Eggs 12pk','Dairy',22.00,32.00,12,5,'2026-07-31',4);

SELECT setval('products_product_id_seq', 5);

CREATE TABLE customers (
  customer_id SERIAL PRIMARY KEY,
  full_name VARCHAR(100) NOT NULL,
  phone VARCHAR(20),
  credit_limit DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  current_balance DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO customers (customer_id, full_name, phone, credit_limit, current_balance, created_date) VALUES
(1,'John Smith','0125677453',100.00,20.00,'2026-05-05 01:00:27');

SELECT setval('customers_customer_id_seq', 1);

CREATE TABLE credit_scores (
  score_id SERIAL PRIMARY KEY,
  user_id INT,
  consistency_score INT,
  volume_score INT,
  growth_score INT,
  final_score INT,
  last_updated DATE,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

INSERT INTO credit_scores (score_id, user_id, consistency_score, volume_score, growth_score, final_score, last_updated) VALUES
(1,1,800,750,775,775,'2026-03-16'),
(2,2,600,500,550,550,'2026-03-16'),
(3,3,900,850,875,875,'2026-03-16'),
(4,4,400,300,350,350,'2026-03-16'),
(5,5,700,720,710,710,'2026-03-16');

SELECT setval('credit_scores_score_id_seq', 5);

CREATE TABLE ai_predictions (
  prediction_id SERIAL PRIMARY KEY,
  product_id INT UNIQUE NOT NULL,
  prediction_type VARCHAR(50) NOT NULL,
  confidence_level DECIMAL(5,2),
  predicted_value VARCHAR(100),
  prediction_date DATE,
  FOREIGN KEY (product_id) REFERENCES products(product_id)
);

INSERT INTO ai_predictions (prediction_id, product_id, prediction_type, confidence_level, predicted_value, prediction_date) VALUES
(1,1,'Demand',0.85,'High','2026-03-16'),
(2,4,'Trend',0.92,'Upward','2026-03-16'),
(3,3,'Demand',0.70,'Low','2026-03-16'),
(4,2,'Trend',0.88,'Stable','2026-03-16'),
(5,5,'Theft Alert',0.65,'Anomaly Detected','2026-03-16');

SELECT setval('ai_predictions_prediction_id_seq', 5);

CREATE TABLE sales (
  sale_id SERIAL PRIMARY KEY,
  product_id INT,
  user_id INT,
  quantity_sold INT NOT NULL,
  total_amount DECIMAL(10,2),
  sale_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (product_id) REFERENCES products(product_id),
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

INSERT INTO sales (sale_id, product_id, user_id, quantity_sold, total_amount, sale_timestamp) VALUES
(1,1,3,2,70.00,'2026-05-05 00:55:22'),
(2,2,4,1,18.50,'2026-05-05 00:55:22'),
(3,4,3,3,45.00,'2026-05-05 00:55:22'),
(4,5,4,1,32.00,'2026-05-05 00:55:22'),
(5,3,3,1,48.00,'2026-05-05 00:55:22'),
(6,3,3,7,336.00,'2026-05-05 01:31:08');

SELECT setval('sales_sale_id_seq', 6);

CREATE TABLE stock_receipts (
  receipt_id SERIAL PRIMARY KEY,
  supplier_id INT NOT NULL,
  product_id INT NOT NULL,
  quantity_received INT NOT NULL,
  received_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  received_by INT,
  FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id),
  FOREIGN KEY (received_by) REFERENCES users(user_id)
);

INSERT INTO stock_receipts (receipt_id, supplier_id, product_id, quantity_received, received_date, received_by) VALUES
(1,4,1,10,'2026-05-05 00:55:22',3),
(2,2,2,20,'2026-05-05 00:55:22',3),
(3,3,4,15,'2026-05-05 00:55:22',4);

SELECT setval('stock_receipts_receipt_id_seq', 3);

CREATE TABLE credit_transactions (
  transaction_id SERIAL PRIMARY KEY,
  customer_id INT NOT NULL,
  product_id INT,
  quantity INT DEFAULT 1,
  amount DECIMAL(10,2) NOT NULL,
  transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('SALE','PAYMENT')),
  transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id)
);

INSERT INTO credit_transactions (transaction_id, customer_id, product_id, quantity, amount, transaction_type, transaction_date) VALUES
(1,1,4,2,30.00,'SALE','2026-05-05 01:00:47'),
(2,1,NULL,1,10.00,'PAYMENT','2026-05-05 01:01:12');

SELECT setval('credit_transactions_transaction_id_seq', 2);
