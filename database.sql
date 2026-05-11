-- Database Export for 'ezasekasi_db'
-- Exported: 2026-05-05 03:03:37
-- Host: 127.0.0.1
-- Database: ezasekasi_db
-- -----------------------------------------------

DROP DATABASE IF EXISTS `ezasekasi_db`;
CREATE DATABASE `ezasekasi_db`;
USE `ezasekasi_db`;

CREATE TABLE `ai_predictions` (
  `prediction_id` int NOT NULL AUTO_INCREMENT,
  `product_id` int DEFAULT NULL,
  `prediction_type` enum('Demand','Trend','Theft Alert') DEFAULT NULL,
  `confidence_level` decimal(5,2) DEFAULT NULL,
  `predicted_value` varchar(100) DEFAULT NULL,
  `prediction_date` date DEFAULT NULL,
  PRIMARY KEY (`prediction_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `ai_predictions_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `ai_predictions` (`prediction_id`, `product_id`, `prediction_type`, `confidence_level`, `predicted_value`, `prediction_date`) VALUES (1, 1, 'Demand', '0.85', 'High', '2026-03-16');
INSERT INTO `ai_predictions` (`prediction_id`, `product_id`, `prediction_type`, `confidence_level`, `predicted_value`, `prediction_date`) VALUES (2, 4, 'Trend', '0.92', 'Upward', '2026-03-16');
INSERT INTO `ai_predictions` (`prediction_id`, `product_id`, `prediction_type`, `confidence_level`, `predicted_value`, `prediction_date`) VALUES (3, 3, 'Demand', '0.70', 'Low', '2026-03-16');
INSERT INTO `ai_predictions` (`prediction_id`, `product_id`, `prediction_type`, `confidence_level`, `predicted_value`, `prediction_date`) VALUES (4, 2, 'Trend', '0.88', 'Stable', '2026-03-16');
INSERT INTO `ai_predictions` (`prediction_id`, `product_id`, `prediction_type`, `confidence_level`, `predicted_value`, `prediction_date`) VALUES (5, 5, 'Theft Alert', '0.65', 'Anomaly Detected', '2026-03-16');

CREATE TABLE `credit_scores` (
  `score_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `consistency_score` int DEFAULT NULL,
  `volume_score` int DEFAULT NULL,
  `growth_score` int DEFAULT NULL,
  `final_score` int DEFAULT NULL,
  `last_updated` date DEFAULT NULL,
  PRIMARY KEY (`score_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `credit_scores_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `credit_scores` (`score_id`, `user_id`, `consistency_score`, `volume_score`, `growth_score`, `final_score`, `last_updated`) VALUES (1, 1, 800, 750, 775, 775, '2026-03-16');
INSERT INTO `credit_scores` (`score_id`, `user_id`, `consistency_score`, `volume_score`, `growth_score`, `final_score`, `last_updated`) VALUES (2, 2, 600, 500, 550, 550, '2026-03-16');
INSERT INTO `credit_scores` (`score_id`, `user_id`, `consistency_score`, `volume_score`, `growth_score`, `final_score`, `last_updated`) VALUES (3, 3, 900, 850, 875, 875, '2026-03-16');
INSERT INTO `credit_scores` (`score_id`, `user_id`, `consistency_score`, `volume_score`, `growth_score`, `final_score`, `last_updated`) VALUES (4, 4, 400, 300, 350, 350, '2026-03-16');
INSERT INTO `credit_scores` (`score_id`, `user_id`, `consistency_score`, `volume_score`, `growth_score`, `final_score`, `last_updated`) VALUES (5, 5, 700, 720, 710, 710, '2026-03-16');

CREATE TABLE `credit_transactions` (
  `transaction_id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int NOT NULL,
  `product_id` int DEFAULT NULL,
  `quantity` int DEFAULT '1',
  `amount` decimal(10,2) NOT NULL,
  `transaction_type` enum('SALE','PAYMENT') NOT NULL,
  `transaction_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`transaction_id`),
  KEY `customer_id` (`customer_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `credit_transactions_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`),
  CONSTRAINT `credit_transactions_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `credit_transactions` (`transaction_id`, `customer_id`, `product_id`, `quantity`, `amount`, `transaction_type`, `transaction_date`) VALUES (1, 1, 4, 2, '30.00', 'SALE', '2026-05-05 01:00:47');
INSERT INTO `credit_transactions` (`transaction_id`, `customer_id`, `product_id`, `quantity`, `amount`, `transaction_type`, `transaction_date`) VALUES (2, 1, NULL, 1, '10.00', 'PAYMENT', '2026-05-05 01:01:12');

CREATE TABLE `customers` (
  `customer_id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(100) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `credit_limit` decimal(10,2) NOT NULL DEFAULT '0.00',
  `current_balance` decimal(10,2) NOT NULL DEFAULT '0.00',
  `created_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`customer_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `customers` (`customer_id`, `full_name`, `phone`, `credit_limit`, `current_balance`, `created_date`) VALUES (1, 'John Smith', '0125677453', '100.00', '20.00', '2026-05-05 01:00:27');

CREATE TABLE `products` (
  `product_id` int NOT NULL AUTO_INCREMENT,
  `product_name` varchar(100) NOT NULL,
  `category` varchar(50) DEFAULT NULL,
  `cost_price` decimal(10,2) DEFAULT NULL,
  `selling_price` decimal(10,2) NOT NULL,
  `stock_quantity` int DEFAULT '0',
  `reorder_level` int DEFAULT '5',
  `expiry_date` date DEFAULT NULL,
  `supplier_id` int DEFAULT NULL,
  PRIMARY KEY (`product_id`),
  KEY `supplier_id` (`supplier_id`),
  CONSTRAINT `products_ibfk_1` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`supplier_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `products` (`product_id`, `product_name`, `category`, `cost_price`, `selling_price`, `stock_quantity`, `reorder_level`, `expiry_date`, `supplier_id`) VALUES (1, 'Milk 2L', 'Dairy', '24.50', '35.00', 20, 5, '2026-12-31', 4);
INSERT INTO `products` (`product_id`, `product_name`, `category`, `cost_price`, `selling_price`, `stock_quantity`, `reorder_level`, `expiry_date`, `supplier_id`) VALUES (2, 'Brown Bread', 'Bakery', '12.00', '18.50', 15, 5, '2026-06-30', 2);
INSERT INTO `products` (`product_id`, `product_name`, `category`, `cost_price`, `selling_price`, `stock_quantity`, `reorder_level`, `expiry_date`, `supplier_id`) VALUES (3, 'Sugar 2kg', 'Pantry', '35.00', '48.00', 3, 5, '2027-01-31', 1);
INSERT INTO `products` (`product_id`, `product_name`, `category`, `cost_price`, `selling_price`, `stock_quantity`, `reorder_level`, `expiry_date`, `supplier_id`) VALUES (4, 'Coke 500ml', 'Beverage', '10.00', '15.00', 48, 10, '2026-11-30', 3);
INSERT INTO `products` (`product_id`, `product_name`, `category`, `cost_price`, `selling_price`, `stock_quantity`, `reorder_level`, `expiry_date`, `supplier_id`) VALUES (5, 'Eggs 12pk', 'Dairy', '22.00', '32.00', 12, 5, '2026-07-31', 4);

CREATE TABLE `sales` (
  `sale_id` int NOT NULL AUTO_INCREMENT,
  `product_id` int DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  `quantity_sold` int NOT NULL,
  `total_amount` decimal(10,2) DEFAULT NULL,
  `sale_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`sale_id`),
  KEY `product_id` (`product_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `sales_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`),
  CONSTRAINT `sales_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `sales` (`sale_id`, `product_id`, `user_id`, `quantity_sold`, `total_amount`, `sale_timestamp`) VALUES (1, 1, 3, 2, '70.00', '2026-05-05 00:55:22');
INSERT INTO `sales` (`sale_id`, `product_id`, `user_id`, `quantity_sold`, `total_amount`, `sale_timestamp`) VALUES (2, 2, 4, 1, '18.50', '2026-05-05 00:55:22');
INSERT INTO `sales` (`sale_id`, `product_id`, `user_id`, `quantity_sold`, `total_amount`, `sale_timestamp`) VALUES (3, 4, 3, 3, '45.00', '2026-05-05 00:55:22');
INSERT INTO `sales` (`sale_id`, `product_id`, `user_id`, `quantity_sold`, `total_amount`, `sale_timestamp`) VALUES (4, 5, 4, 1, '32.00', '2026-05-05 00:55:22');
INSERT INTO `sales` (`sale_id`, `product_id`, `user_id`, `quantity_sold`, `total_amount`, `sale_timestamp`) VALUES (5, 3, 3, 1, '48.00', '2026-05-05 00:55:22');
INSERT INTO `sales` (`sale_id`, `product_id`, `user_id`, `quantity_sold`, `total_amount`, `sale_timestamp`) VALUES (6, 3, 3, 7, '336.00', '2026-05-05 01:31:08');

CREATE TABLE `stock_receipts` (
  `receipt_id` int NOT NULL AUTO_INCREMENT,
  `supplier_id` int NOT NULL,
  `product_id` int NOT NULL,
  `quantity_received` int NOT NULL,
  `received_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `received_by` int DEFAULT NULL,
  PRIMARY KEY (`receipt_id`),
  KEY `supplier_id` (`supplier_id`),
  KEY `product_id` (`product_id`),
  KEY `received_by` (`received_by`),
  CONSTRAINT `stock_receipts_ibfk_1` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`supplier_id`),
  CONSTRAINT `stock_receipts_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`),
  CONSTRAINT `stock_receipts_ibfk_3` FOREIGN KEY (`received_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `stock_receipts` (`receipt_id`, `supplier_id`, `product_id`, `quantity_received`, `received_date`, `received_by`) VALUES (1, 4, 1, 10, '2026-05-05 00:55:22', 3);
INSERT INTO `stock_receipts` (`receipt_id`, `supplier_id`, `product_id`, `quantity_received`, `received_date`, `received_by`) VALUES (2, 2, 2, 20, '2026-05-05 00:55:22', 3);
INSERT INTO `stock_receipts` (`receipt_id`, `supplier_id`, `product_id`, `quantity_received`, `received_date`, `received_by`) VALUES (3, 3, 4, 15, '2026-05-05 00:55:22', 4);

CREATE TABLE `suppliers` (
  `supplier_id` int NOT NULL AUTO_INCREMENT,
  `company_name` varchar(100) NOT NULL,
  `contact_person` varchar(100) DEFAULT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`supplier_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `suppliers` (`supplier_id`, `company_name`, `contact_person`, `phone`, `email`) VALUES (1, 'Tshwane Wholesalers', 'Mr. Dube', '0125550001', NULL);
INSERT INTO `suppliers` (`supplier_id`, `company_name`, `contact_person`, `phone`, `email`) VALUES (2, 'Emalahleni Bakery', 'Sarah', '0135559999', NULL);
INSERT INTO `suppliers` (`supplier_id`, `company_name`, `contact_person`, `phone`, `email`) VALUES (3, 'Beverage Corp', 'John', '0114441111', NULL);
INSERT INTO `suppliers` (`supplier_id`, `company_name`, `contact_person`, `phone`, `email`) VALUES (4, 'Dairy Fresh', 'Lerato', '0127778888', NULL);
INSERT INTO `suppliers` (`supplier_id`, `company_name`, `contact_person`, `phone`, `email`) VALUES (5, 'Agri-Nathi Logistics', 'Thabo', '0153332222', NULL);

CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(100) NOT NULL,
  `user_role` enum('Owner','Cashier','Supplier','Admin') NOT NULL,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `contact_number` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `users` (`user_id`, `full_name`, `user_role`, `username`, `password_hash`, `contact_number`) VALUES (1, 'Mercy Molonyama', 'Owner', 'mercy_m', '123456', NULL);
INSERT INTO `users` (`user_id`, `full_name`, `user_role`, `username`, `password_hash`, `contact_number`) VALUES (2, 'Happiness Simao', 'Admin', 'happy_s', '123456', NULL);
INSERT INTO `users` (`user_id`, `full_name`, `user_role`, `username`, `password_hash`, `contact_number`) VALUES (3, 'Brightness Masilela', 'Cashier', 'bri_m', '123456', NULL);
INSERT INTO `users` (`user_id`, `full_name`, `user_role`, `username`, `password_hash`, `contact_number`) VALUES (4, 'Kearabetswe Lebelo', 'Cashier', 'kea_l', '123456', NULL);
INSERT INTO `users` (`user_id`, `full_name`, `user_role`, `username`, `password_hash`, `contact_number`) VALUES (5, 'Karabo Komane', 'Supplier', 'kaybee_k', '123456', NULL);
INSERT INTO `users` (`user_id`, `full_name`, `user_role`, `username`, `password_hash`, `contact_number`) VALUES (6, 'Tau Thamaga', 'Cashier', 'tau_t', '123456', NULL);
INSERT INTO `users` (`user_id`, `full_name`, `user_role`, `username`, `password_hash`, `contact_number`) VALUES (7, 'Percy Thotse', 'Cashier', 'percy_t', '123456', NULL);
INSERT INTO `users` (`user_id`, `full_name`, `user_role`, `username`, `password_hash`, `contact_number`) VALUES (8, 'Tshwarelo Mahlako', 'Admin', 'tshwarelo_m', '123456', NULL);
INSERT INTO `users` (`user_id`, `full_name`, `user_role`, `username`, `password_hash`, `contact_number`) VALUES (9, 'Samkelisiwe Mngadi', 'Cashier', 'samke_m', '123456', NULL);

