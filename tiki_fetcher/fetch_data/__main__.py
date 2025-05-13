import time
import logging

from tiki_fetcher.fetch_data.collect_products import collect_data

if __name__ == "__main__":
    start_time = time.time()
    try:
        collect_data("id_product.csv")
    except Exception as e:
        logging.exception("Unexpected error when collecting data")
    end_time = time.time()
    duration = end_time - start_time
    logging.info(f"\nCompleted in {duration:.2f} seconds")