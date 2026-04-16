
  
  create view "warehouse"."main"."stg_products__dbt_tmp" as (
    SELECT
    cast(product_id AS varchar) AS product_id,
    cast(product_name AS varchar) AS product_name,
    cast(category AS varchar) AS category,
    cast(price AS double) AS price,
    cast(currency AS varchar) AS currency,
    cast(is_active AS boolean) AS is_active,
    cast(source_file AS varchar) AS source_file
FROM
    "warehouse"."main"."products"
WHERE
    product_id IS NOT NULL
    AND trim(product_id) <> ''
  );
