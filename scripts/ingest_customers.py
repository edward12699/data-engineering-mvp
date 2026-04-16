import duckdb
import pandas as pd
from pathlib import Path

DB_PATH = "data/warehouse.duckdb"
CSV_PATH = "data/raw/customers.csv"

def ingest_customers():
    con = duckdb.connect(DB_PATH)
    df = pd.read_csv(CSV_PATH)

    file_name = Path(CSV_PATH).name
    df["source_file"] = file_name

    # 1) 原始落地表
    con.execute("""
        create table if not exists customers (
            customer_id varchar,
            full_name varchar,
            email varchar,
            signup_date varchar,
            country varchar,
            city varchar,
            is_active boolean
        )
    """)
    con.execute("alter table customers add column if not exists source_file varchar")

    # 2) 先放到临时表
    con.register("customers_df", df)

    # 3) 增量插入：按 customer_id 去重，过滤空值，并避免 NOT IN + NULL 的坑
    con.execute("""
        insert into customers (
            customer_id,
            full_name,
            email,
            signup_date,
            country,
            city,
            is_active,
            source_file
        )
        select
            s.customer_id,
            s.full_name,
            s.email,
            s.signup_date,
            s.country,
            s.city,
            cast(s.is_active as boolean),
            s.source_file
        from (
            select *
            from customers_df
            where customer_id is not null and trim(customer_id) <> ''
            qualify row_number() over (partition by customer_id order by signup_date desc) = 1
        ) as s
        where not exists (
            select 1
            from customers t
            where t.customer_id = s.customer_id
        )
    """)

    count = con.execute("select count(*) from customers").fetchone()[0]
    print(f"customers rows: {count}")

if __name__ == "__main__":
    ingest_customers()
