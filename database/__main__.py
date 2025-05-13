import psycopg2
from database.config import load_config
from database.db_handle import insert_data

if __name__ == "__main__":
    insert_data() # call insert function to insert all data into the table in DTB

    # check the number of data in the table: expected output: 198942
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                                select* from products;
                            """)
                rows = cur.rowcount
                print(rows)
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)
