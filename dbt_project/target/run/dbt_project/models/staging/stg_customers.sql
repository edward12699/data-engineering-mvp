
  
  create view "warehouse"."main"."stg_customers__dbt_tmp" as (
    SELECT
    cast(customer_id AS varchar) AS customer_id,
    cast(full_name AS varchar) AS full_name,
    cast(email AS varchar) AS email,
    cast(signup_date AS date) AS signup_date,
    cast(country AS varchar) AS country,
    cast(city AS varchar) AS city,
    cast(is_active AS boolean) AS is_active,
    cast(source_file AS varchar) AS source_file
FROM
    "warehouse"."main"."customers"
WHERE
    customer_id IS NOT NULL
    AND trim(customer_id) <> ''
  );
