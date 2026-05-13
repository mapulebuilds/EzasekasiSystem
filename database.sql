DROP DATABASE IF EXISTS ezasekasi_db;
CREATE DATABASE ezasekasi_db;
USE ezasekasi_db;

CREATE TABLE users (
  user_id INT NOT NULL AUTO_INCREMENT,
  full_name VARCHAR(100) NOT NULL,
  user_role ENUM('Owner','Cashier','Supplier','Admin') NOT NULL,
  username VARCHAR(50) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  contact_number VARCHAR(15),
  PRIMARY KEY (user_id)
) ENGINE=InnoDB AUTO_INCREMENT=10;

INSERT INTO users VALUES
(1,'Mercy Molonyama','Owner','mercy_m','123456',NULL),
(2,'Happiness Simao','Admin','happy_s','123456',NULL),
(3,'Brightness Masilela','Cashier','bri_m','123456',NULL),
(4,'Kearabetswe Lebelo','Cashier','kea_l','123456',NULL),
(5,'Karabo Komane','Supplier','kaybee_k','123456',NULL),
(6,'Tau Thamaga','Cashier','tau_t','123456',NULL),
(7,'Percy Thotse','Cashier','percy_t','123456',NULL),
(8,'Tshwarelo Mahlako','Admin','tshwarelo_m','123456',NULL),
(9,'Samkelisiwe Mngadi','Cashier','samke_m','123456',NULL);

CREATE TABLE suppliers (
  supplier_id INT NOT NULL AUTO_INCREMENT,
  company_name VARCHAR(100) NOT NULL,
  contact_person VARCHAR(100),
  phone VARCHAR(15),
  email VARCHAR(100),
  PRIMARY KEY (supplier_id)
) ENGINE=InnoDB AUTO_INCREMENT=6;

INSERT INTO suppliers VALUES
(1,'Tshwane Wholesalers','Mr. Dube','0125550001',NULL),
(2,'Emalahleni Bakery','Sarah','0135559999',NULL),
(3,'Beverage Corp','John','0114441111',NULL),
(4,'Dairy Fresh','Lerato','0127778888',NULL),
(5,'Agri-Nathi Logistics','Thabo','0153332222',NULL);

CREATE TABLE products (
  product_id INT NOT NULL AUTO_INCREMENT,
  product_name VARCHAR(100) NOT NULL,
  category VARCHAR(50),
  cost_price DECIMAL(10,2),
  selling_price DECIMAL(10,2) NOT NULL,
  stock_quantity INT DEFAULT 0,
  reorder_level INT DEFAULT 5,
  expiry_date DATE,
  supplier_id INT,
  PRIMARY KEY (product_id),
  FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
) ENGINE=InnoDB AUTO_INCREMENT=6;

INSERT INTO products VALUES
(1,'Milk 2L','Dairy',24.50,35.00,20,5,'2026-12-31',4),
(2,'Brown Bread','Bakery',12.00,18.50,15,5,'2026-06-30',2),
(3,'Sugar 2kg','Pantry',35.00,48.00,3,5,'2027-01-31',1),
(4,'Coke 500ml','Beverage',10.00,15.00,48,10,'2026-11-30',3),
(5,'Eggs 12pk','Dairy',22.00,32.00,12,5,'2026-07-31',4);

CREATE TABLE customers (
  customer_id INT NOT NULL AUTO_INCREMENT,
  full_name VARCHAR(100) NOT NULL,
  phone VARCHAR(20),
  credit_limit DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  current_balance DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (customer_id)
) ENGINE=InnoDB AUTO_INCREMENT=2;

INSERT INTO customers VALUES
(1,'John Smith','0125677453',100.00,20.00,'2026-05-05 01:00:27');

CREATE TABLE credit_scores (
  score_id INT NOT NULL AUTO_INCREMENT,
  user_id INT,
  consistency_score INT,
  volume_score INT,
  growth_score INT,
  final_score INT,
  last_updated DATE,
  PRIMARY KEY (score_id),
  FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB AUTO_INCREMENT=6;

INSERT INTO credit_scores VALUES
(1,1,800,750,775,775,'2026-03-16'),
(2,2,600,500,550,550,'2026-03-16'),
(3,3,900,850,875,875,'2026-03-16'),
(4,4,400,300,350,350,'2026-03-16'),
(5,5,700,720,710,710,'2026-03-16');

CREATE TABLE ai_predictions (
  prediction_id INT NOT NULL AUTO_INCREMENT,
  product_id INT,
  prediction_type ENUM('Demand','Trend','Theft Alert'),
  confidence_level DECIMAL(5,2),
  predicted_value VARCHAR(100),
  prediction_date DATE,
  PRIMARY KEY (prediction_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id)
) ENGINE=InnoDB AUTO_INCREMENT=6;

INSERT INTO ai_predictions VALUES
(1,1,'Demand',0.85,'High','2026-03-16'),
(2,4,'Trend',0.92,'Upward','2026-03-16'),
(3,3,'Demand',0.70,'Low','2026-03-16'),
(4,2,'Trend',0.88,'Stable','2026-03-16'),
(5,5,'Theft Alert',0.65,'Anomaly Detected','2026-03-16');

CREATE TABLE sales (
  sale_id INT NOT NULL AUTO_INCREMENT,
  product_id INT,
  user_id INT,
  quantity_sold INT NOT NULL,
  total_amount DECIMAL(10,2),
  sale_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (sale_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id),
  FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB AUTO_INCREMENT=7;

INSERT INTO sales VALUES
(1,1,3,2,70.00,'2026-05-05 00:55:22'),
(2,2,4,1,18.50,'2026-05-05 00:55:22'),
(3,4,3,3,45.00,'2026-05-05 00:55:22'),
(4,5,4,1,32.00,'2026-05-05 00:55:22'),
(5,3,3,1,48.00,'2026-05-05 00:55:22'),
(6,3,3,7,336.00,'2026-05-05 01:31:08');

CREATE TABLE stock_receipts (
  receipt_id INT NOT NULL AUTO_INCREMENT,
  supplier_id INT NOT NULL,
  product_id INT NOT NULL,
  quantity_received INT NOT NULL,
  received_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  received_by INT,
  PRIMARY KEY (receipt_id),
  FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id),
  FOREIGN KEY (received_by) REFERENCES users(user_id)
) ENGINE=InnoDB AUTO_INCREMENT=4;

INSERT INTO stock_receipts VALUES
(1,4,1,10,'2026-05-05 00:55:22',3),
(2,2,2,20,'2026-05-05 00:55:22',3),
(3,3,4,15,'2026-05-05 00:55:22',4);

CREATE TABLE credit_transactions (
  transaction_id INT NOT NULL AUTO_INCREMENT,
  customer_id INT NOT NULL,
  product_id INT,
  quantity INT DEFAULT 1,
  amount DECIMAL(10,2) NOT NULL,
  transaction_type ENUM('SALE','PAYMENT') NOT NULL,
  transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (transaction_id),
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id)
) ENGINE=InnoDB AUTO_INCREMENT=3;

INSERT INTO credit_transactions VALUES
(1,1,4,2,30.00,'SALE','2026-05-05 01:00:47'),
(2,1,NULL,1,10.00,'PAYMENT','2026-05-05 01:01:12');