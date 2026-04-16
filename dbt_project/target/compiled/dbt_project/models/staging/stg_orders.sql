SELECT
    cast(order_id AS varchar) AS order_id,
    cast(customer_id AS varchar) AS customer_id,
    cast(product_id AS varchar) AS product_id,
    cast(quantity AS int) AS quantity,
    cast(unit_price AS double) AS unit_price,
    cast(discount AS double) AS discount,
    cast(order_status AS varchar) AS order_status,
    cast(payment_method AS varchar) AS payment_method,
    cast(order_date AS date) AS order_date
FROM
    "warehouse"."main"."orders"
WHERE
    order_id IS NOT NULL
    AND trim(order_id) <> ''