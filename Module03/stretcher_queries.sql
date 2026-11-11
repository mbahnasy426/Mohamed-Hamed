-- 1. Baseline GROUP BY late orders
SELECT c.customer_id, c.name, COUNT(*) AS late_orders
FROM orders AS o JOIN customer AS c ON c.customer_id = o.customer_id
WHERE o.status = 'late'
GROUP BY c.customer_id, c.name
ORDER BY late_orders DESC, c.customer_id;

-- 2. Correlated subquery with EXISTS
SELECT c.customer_id, c.name,
       (SELECT COUNT(*) FROM orders AS o
        WHERE o.customer_id = c.customer_id AND o.status = 'late') AS late_orders
FROM customer AS c
WHERE EXISTS (
    SELECT 1 FROM orders AS o
    WHERE o.customer_id = c.customer_id AND o.status = 'late'
)
ORDER BY late_orders DESC, c.customer_id;

-- 3. Window function; ROW_NUMBER removes per-order duplicates
WITH ranked AS (
  SELECT c.customer_id, c.name,
         COUNT(*) OVER (PARTITION BY c.customer_id) AS late_orders,
         ROW_NUMBER() OVER (PARTITION BY c.customer_id ORDER BY o.order_id) AS rn
  FROM orders AS o JOIN customer AS c ON c.customer_id = o.customer_id
  WHERE o.status = 'late'
)
SELECT customer_id, name, late_orders
FROM ranked WHERE rn = 1
ORDER BY late_orders DESC, customer_id;
