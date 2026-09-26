import pandas as pd
import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root123',
    'database': 'directory_scraper'
}

def export_to_csv():
    conn = pymysql.connect(**DB_CONFIG)
    query = "SELECT * FROM extracted_architects"
    df = pd.read_sql(query, conn)
    df.to_csv("data/dataset_snapshot.csv", index=False)
    print("✅ Exported dataset snapshot to data/dataset_snapshot.csv")
    conn.close()

if __name__ == "__main__":
    export_to_csv()
