CREATE DATABASE IF NOT EXISTS restaurant;
USE restaurant;

DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS shifts;
DROP TABLE IF EXISTS menu_items;
DROP TABLE IF EXISTS employees;

CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL
);

CREATE TABLE menu_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    item_type ENUM('appetizer','main','dessert','beverage') NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    vat_percentage TINYINT NOT NULL,
    vat DECIMAL(10,2)
);

DELIMITER $$

CREATE TRIGGER menu_items_calc_vat_ins
BEFORE INSERT ON menu_items
FOR EACH ROW
BEGIN
    SET NEW.vat = ROUND(NEW.price * NEW.vat_percentage / 100, 2);
END$$

CREATE TRIGGER menu_items_calc_vat_upd
BEFORE UPDATE ON menu_items
FOR EACH ROW
BEGIN
    SET NEW.vat = ROUND(NEW.price * NEW.vat_percentage / 100, 2);
END$$

DELIMITER ;

CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NULL,
    employee_first_name VARCHAR(255),
    employee_last_name VARCHAR(255),
    name varchar(255) NOT NULL,
    creation_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_paid TINYINT NOT NULL,
    total_price DECIMAL(10,2) DEFAULT 0,
    total_vat DECIMAL(10,2) DEFAULT 0,
    FOREIGN KEY (employee_id)
    REFERENCES employees(id)
    ON DELETE SET NULL
);

DELIMITER $$

CREATE TRIGGER orders_snapshot_employee
BEFORE INSERT ON orders
FOR EACH ROW
BEGIN
    IF NEW.employee_id IS NOT NULL THEN
        SET NEW.employee_first_name = (SELECT first_name FROM employees WHERE id = NEW.employee_id);
        SET NEW.employee_last_name = (SELECT last_name FROM employees WHERE id = NEW.employee_id);
    END IF;
END$$

DELIMITER ;

CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    menu_item_id INT NULL,
    item_name VARCHAR(255) NOT NULL,
    item_type ENUM('appetizer','main','dessert','beverage') NOT NULL,
    item_price DECIMAL(10,2) NOT NULL,
    vat_percentage TINYINT NOT NULL,
    item_vat DECIMAL(10,2) NOT NULL,
    quantity INT NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    total_vat DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id)
    REFERENCES orders(id)
    ON DELETE CASCADE,
    FOREIGN KEY (menu_item_id)
    REFERENCES menu_items(id)
    ON DELETE SET NULL
);

DELIMITER $$

CREATE TRIGGER order_items_snapshot_menu_item
BEFORE INSERT ON order_items
FOR EACH ROW
BEGIN
    SET NEW.item_name = (SELECT name FROM menu_items WHERE id = NEW.menu_item_id);
    SET NEW.item_type = (SELECT item_type FROM menu_items WHERE id = NEW.menu_item_id);
    SET NEW.item_price = (SELECT price FROM menu_items WHERE id = NEW.menu_item_id);
    SET NEW.vat_percentage = (SELECT vat_percentage FROM menu_items WHERE id = NEW.menu_item_id);
    SET NEW.item_vat = (SELECT vat FROM menu_items WHERE id = NEW.menu_item_id);
    SET NEW.total_price = NEW.item_price * NEW.quantity;
    SET NEW.total_vat = NEW.item_vat * NEW.quantity;
END$$

CREATE TRIGGER order_items_recalc_totals_upd
BEFORE UPDATE ON order_items
FOR EACH ROW
BEGIN
    SET NEW.total_price = NEW.item_price * NEW.quantity;
    SET NEW.total_vat = NEW.item_vat * NEW.quantity;
END$$

CREATE TRIGGER orders_update_totals_ins
AFTER INSERT ON order_items
FOR EACH ROW
BEGIN
    UPDATE orders
    SET total_price = IFNULL((SELECT SUM(total_price) FROM order_items WHERE order_id = NEW.order_id), 0),
        total_vat = IFNULL((SELECT SUM(total_vat) FROM order_items WHERE order_id = NEW.order_id), 0)
    WHERE id = NEW.order_id;
END$$

CREATE TRIGGER orders_update_totals_upd
AFTER UPDATE ON order_items
FOR EACH ROW
BEGIN
    UPDATE orders
    SET total_price = IFNULL((SELECT SUM(total_price) FROM order_items WHERE order_id = NEW.order_id), 0),
        total_vat = IFNULL((SELECT SUM(total_vat) FROM order_items WHERE order_id = NEW.order_id), 0)
    WHERE id = NEW.order_id;
    
    IF OLD.order_id <> NEW.order_id THEN
        UPDATE orders
        SET total_price = IFNULL((SELECT SUM(total_price) FROM order_items WHERE order_id = OLD.order_id), 0),
            total_vat = IFNULL((SELECT SUM(total_vat) FROM order_items WHERE order_id = OLD.order_id), 0)
        WHERE id = OLD.order_id;
    END IF;
END$$

CREATE TRIGGER orders_update_totals_del
AFTER DELETE ON order_items
FOR EACH ROW
BEGIN
    UPDATE orders
    SET total_price = IFNULL((SELECT SUM(total_price) FROM order_items WHERE order_id = OLD.order_id), 0),
        total_vat = IFNULL((SELECT SUM(total_vat) FROM order_items WHERE order_id = OLD.order_id), 0)
    WHERE id = OLD.order_id;
END$$

DELIMITER ;

CREATE TABLE shifts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NULL,
    employee_first_name VARCHAR(255) NOT NULL,
    employee_last_name VARCHAR(255) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    hourly_rate DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (employee_id)
    REFERENCES employees(id)
    ON DELETE SET NULL
);

DELIMITER $$

CREATE TRIGGER shifts_snapshot_employee
BEFORE INSERT ON shifts
FOR EACH ROW
BEGIN
    IF NEW.employee_id IS NOT NULL THEN
        SET NEW.employee_first_name = (SELECT first_name FROM employees WHERE id = NEW.employee_id);
        SET NEW.employee_last_name = (SELECT last_name FROM employees WHERE id = NEW.employee_id);
    END IF;
END$$

DELIMITER ;

CREATE OR REPLACE VIEW view_shifts_log AS
SELECT 
    id, 
    employee_id, 
    employee_first_name, 
    employee_last_name, 
    start_time, 
    end_time, 
    hourly_rate,
    DATE(start_time) as shift_date
FROM shifts;

CREATE OR REPLACE VIEW view_paid_orders AS
SELECT 
    id, 
    employee_id, 
    employee_first_name, 
    employee_last_name, 
    name, 
    creation_date, 
    is_paid, 
    total_price, 
    total_vat
FROM orders 
WHERE is_paid = 0;

CREATE OR REPLACE VIEW view_product_sales_report AS
SELECT 
    mi.item_type AS category,
    mi.name AS product_name,
    COUNT(DISTINCT o.id) AS orders_count,     
    SUM(oi.quantity) AS total_quantity_sold,  
    SUM(oi.total_price) AS total_revenue 
FROM menu_items mi
JOIN order_items oi ON mi.id = oi.menu_item_id
JOIN orders o ON oi.order_id = o.id
GROUP BY mi.item_type, mi.name
ORDER BY total_revenue DESC;