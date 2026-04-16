# import duckdb
# import pandas as pd

# con = duckdb.connect("data/warehouse.duckdb")

# df = pd.read_csv("data/raw/orders.csv")

# con.execute("CREATE TABLE IF NOT EXISTS orders AS SELECT * FROM df")

# 当前脚本缺点
# 	1.	CREATE TABLE IF NOT EXISTS 只能首次建表，后续重复执行不会刷新数据。 ￼
# 	2.	没有区分“首次加载”和“增量加载”。
# 	3.	没有基于 order_id 做去重或 upsert。
# 	4.	没有记录批次信息，无法追踪这次导入来自哪个文件。
# 	5.	没有日志和异常处理，失败后不方便排查。

# 这就像数据工程师说的话了。


import duckdb
import pandas as pd
from pathlib import Path

DB_PATH = "data/warehouse.duckdb"
CSV_PATH = "data/raw/orders.csv"

def ingest_orders():
    con = duckdb.connect(DB_PATH)
    df = pd.read_csv(CSV_PATH)

    file_name = Path(CSV_PATH).name
    df["source_file"] = file_name

    # 1) 原始落地表
    con.execute("""
        create table if not exists orders (
            order_id varchar,
            order_date varchar,
            customer_id varchar,
            product_id varchar,
            quantity varchar,
            unit_price varchar,
            discount varchar,
            order_status varchar,
            payment_method varchar,
            source_file varchar
        )
    """)

    # 2) 先放到临时表
    con.register("orders_df", df)

    # 3) 插入时按 order_id 去重（最简版）
    con.execute("""
        insert into orders
        select *
        from orders_df
        where order_id not in (
          select order_id from orders
          where order_id is not null and trim(order_id) <> ''
        )
    """)

    count = con.execute("select count(*) from orders").fetchone()[0]
    print(f"orders rows: {count}")

if __name__ == "__main__":
    ingest_orders()
