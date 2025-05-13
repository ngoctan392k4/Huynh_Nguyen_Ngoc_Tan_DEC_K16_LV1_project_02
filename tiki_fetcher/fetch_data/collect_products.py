import os
import csv
from multiprocessing import Pool
from tqdm import tqdm
from tiki_fetcher.fetch_data.config import load_config
from tiki_fetcher.fetch_data.fetch import fetch_data
from tiki_fetcher.fetch_data.save import save_404_error, save_batch_data, save_checkpoint, save_http_error, save_timeout_error

config = load_config()
log_cfg = config.get("LOGGING", {})

def collect_data(input_csv_file, batch_size=config["BATCH_SIZE"]):
    # Get the latest batch to continue
    start_batch = load_checkpoint()

    def batch_reader(input_csv_file, batch_size, start_batch):
        with open(input_csv_file, "r", encoding="utf-8") as rf:
            reader = csv.DictReader(rf)
            all_ids = [row["product_id"] for row in reader if row["product_id"]]

        start_index = (start_batch - 1) * batch_size # calculate the first position to fetch
        batch_num = start_batch

        for i in range(start_index, len(all_ids), batch_size):
            batch = all_ids[i:i + batch_size] # Get ids from i to i + batch_size
            yield batch, batch_num
            batch_num += 1

    # Traverse batch one by one
    for batch, batch_num in batch_reader(input_csv_file, batch_size, start_batch):
        collected_data = []
        error_404_code = []
        http_error = []
        timeout_error = []

        # Process with 40 product ids at the same time => faster
        # imap_unordered allows it receive fetched data without ordering => No wait => faster
        with Pool(processes=config["POOL_SIZE"]) as pool:
            for result in tqdm(pool.imap_unordered(fetch_data, batch), total=len(batch)):
                if isinstance(result, dict) and "status" in result:
                    if result["status"] == "http_error":
                        http_error.append((result["product_id"], result["code"]))
                    elif result["status"] == "404_error":
                        error_404_code.append((result["product_id"], result["code"]))
                    elif result["status"] == "timeout_error":
                        timeout_error.append(result["product_id"])

                else:
                    collected_data.append(result)

        save_batch_data(collected_data, batch_num)
        save_404_error(error_404_code)
        save_http_error(http_error)
        save_timeout_error(timeout_error)
        save_checkpoint(batch_num+1)



# read checkpoint to get the latest batch => continue fetch data with the latest batch
def load_checkpoint():
    if os.path.exists("data/checkpoint/checkpoint.txt"):
        with open("data/checkpoint/checkpoint.txt", "r", encoding="utf-8") as rf:
            return int(rf.read())
    else:
        return 1