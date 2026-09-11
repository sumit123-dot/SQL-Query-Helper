create database sql_helper;
use sql_hepler;

CREATE TABLE sales(
    sale_id INT PRIMARY KEY AUTO_INCREMENT,
    sale_date DATE,
    product_id INT,
    product_name VARCHAR(100),
    category VARCHAR(100),
    quantity INT,
    unit_price DECIMAL(10,2),
    sales_amount DECIMAL(10,2),
    customer_city VARCHAR(100)
);

INSERT INTO sales
(sale_date, product_id, product_name, category, quantity, unit_price, sales_amount, customer_city)
VALUES
('2026-08-01', 101, 'Laptop', 'Electronics', 2, 55000, 110000, 'Pune'),

('2026-08-02', 102, 'Mouse', 'Electronics', 10, 800, 8000, 'Mumbai'),

('2026-08-03', 103, 'Keyboard', 'Electronics', 5, 1500, 7500, 'Pune'),

('2026-08-04', 104, 'Monitor', 'Electronics', 3, 12000, 36000, 'Nashik'),

('2026-08-05', 105, 'Headphones', 'Accessories', 8, 2500, 20000, 'Mumbai'),

('2026-08-06', 106, 'Printer', 'Office', 2, 18000, 36000, 'Pune'),

('2026-08-07', 107, 'Tablet', 'Electronics', 4, 22000, 88000, 'Nagpur'),

('2026-08-08', 108, 'Webcam', 'Accessories', 6, 3000, 18000, 'Pune'),

('2026-08-09', 109, 'Chair', 'Furniture', 5, 7000, 35000, 'Mumbai'),

('2026-08-10', 110, 'Desk', 'Furniture', 3, 10000, 30000, 'Nashik');

select * from sales;

SELECT SUM(sales_amount) AS total_sales
FROM sales;
SELECT product_name, SUM(sales_amount) AS total_sales
FROM sales
GROUP BY product_name
ORDER BY total_sales DESC;

SELECT customer_city, SUM(sales_amount) AS total_sales
FROM sales
GROUP BY customer_city
ORDER BY total_sales DESC;
show tables;