SELECT customers.CustomerID, orders.CustomerID
FROM customers
INNER JOIN orders
ON customers.CustomerID = orders.CustomerID
WHERE customers.CustomerID