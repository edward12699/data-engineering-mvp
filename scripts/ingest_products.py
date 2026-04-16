import duckdb
import pandas as pd
from pathlib import Path

DB_PATH = "data/warehouse.duckdb"
CSV_PATH = "data/raw/products.csv"

def ingest_products():
    con = duckdb.connect(DB_PATH)
    df = pd.read_csv(CSV_PATH)

    file_name = Path(CSV_PATH).name
    df["source_file"] = file_name

    # 1) 原始落地表
    con.execute("""
        create table if not exists products (
            product_id varchar,
            product_name varchar,
            category varchar,
            price double,
            currency varchar,
            is_active boolean
        )
    """)
    con.execute("alter table products add column if not exists source_file varchar")

    # 2) 先放到临时表
    con.register("products_df", df)

    # 3) 增量插入：按 product_id 去重，过滤空值，并避免 NOT IN + NULL 的坑
    con.execute("""
        insert into products (
            product_id,
            product_name,
            category,
            price,
            currency,
            is_active,
            source_file
        )
        select
            s.product_id,
            s.product_name,
            s.category,
            cast(s.price as double),
            s.currency,
            cast(s.is_active as boolean),
            s.source_file
        from (
            select *
            from products_df
            where product_id is not null and trim(product_id) <> ''
            qualify row_number() over (partition by product_id order by product_id) = 1
        ) as s
        where not exists (
            select 1
            from products t
            where t.product_id = s.product_id
        )
    """)

    count = con.execute("select count(*) from products").fetchone()[0]
    print(f"products rows: {count}")

if __name__ == "__main__":
    ingest_products()