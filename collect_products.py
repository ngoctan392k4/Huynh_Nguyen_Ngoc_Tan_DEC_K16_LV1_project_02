import requests
import os
import time
import csv
import json
from multiprocessing import Pool
from tqdm import tqdm

def fetch_data(product_id):
    max_tries = 5 # if catch errors, try again until attempt = 5
    for attempt in range(max_tries):
        try:
            # Ensure that we request API like a real person
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/112.0.0.0 Safari/537.36"
            }
            response = requests.get("https://api.tiki.vn/product-detail/api/v1/products/{}".format(product_id), headers=headers, timeout=15)

            if response.status_code == 200:
                data = response.json()

                # If images do not exist return empty
                images = data.get("images")
                if images and isinstance (images, list):
                    images_url = [img.get("base_url") for img in images if img.get("base_url")]
                else:
                    images_url = []

                return {
                    "id": data.get("id"),
                    "name": data.get("name"),
                    "url_key": data.get("url_key"),
                    "price": data.get("price"),
                    "description": data.get("description"),
                    "images": images_url
                }

            else:
                if response.status_code == 404:
                    return {
                        "status": "404_error",
                        "product_id": product_id,
                        "code": response.status_code
                    }
                else:
                    if attempt == max_tries - 1:
                        return {
                            "status": "http_error",
                            "product_id": product_id,
                            "code": response.status_code
                        }
                    else:
                        time.sleep(2)
        except requests.RequestException as e:
            print(f"Attempt {attempt+1} with product id {product_id}: {e}")
            if attempt == max_tries - 1:
                return {
                    "status": "timeout_error",
                    "product_id": product_id
                }
            else:
                time.sleep(2)

def collect_data(input_csv_file, batch_size=1000):
    # Get the latest batch to continue
    start_batch = load_checkpoint()

    # Get the product into the batch - ensure that it is the latest batch to continue to fetch data
    def batch_reader(reader, batch_size, start_batch):
        batch = []
        batch_num = 1
        for row in reader:
            pd_id = row["product_id"]
            if pd_id:
                # if it is not the latest batch, store id and the remove out of batch => ensure that we get the first item in the latest batch
                if batch_num < start_batch:
                    if len(batch) < batch_size:
                        batch.append(pd_id)
                    if len(batch) == batch_size:
                        batch = []
                        batch_num += 1
                    continue

                # if it is the latest batch => get IDs
                batch.append(pd_id)
                if len(batch) == batch_size:
                    yield batch, batch_num
                    batch = []
                    batch_num +=1
        # At the end, if there is not enough 1000 IDs, still return to fetch data
        if batch:
            yield batch, batch_num


    with open(input_csv_file, "r", encoding="utf-8") as rf:
        reader = csv.DictReader(rf)

        # Traverse batch one by one
        for batch, batch_num in batch_reader(reader, batch_size, start_batch):
            collected_data = []
            error_404_code = []
            http_error = []
            timeout_error = []

            # Process with 40 product ids at the same time => faster
            # imap_unordered allows it receive fetched data without ordering => No wait => faster
            with Pool(processes=40) as pool:
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

# save product in the current batch into the .json file
def save_batch_data(data, batch_num):
    os.makedirs("output_raw", exist_ok=True)
    with open(f"output_raw/products_batch_{batch_num}.json", "w", encoding="utf-8") as wf:
        json.dump(data, wf, ensure_ascii=False, indent=2)
    print(f"Have saved {len(data)} products in batch {batch_num} into output_raw/products_batch_{batch_num}.json")

# save all product ids that receive http error
def save_http_error(data):
    os.makedirs("output_raw/error", exist_ok=True)
    check_not_exist = not os.path.exists("output_raw/error/http_error.csv")
    with open("output_raw/error/http_error.csv", "a", encoding="utf-8", newline="") as wf:
        writer = csv.writer(wf)
        if check_not_exist:
            writer.writerow(["product_id", "code"])
        for pd_id, code in data:
            writer.writerow([pd_id, code])
    print(f"Have saved {len(data)} HTTP errors into output_raw/error/http_error.csv")

# save all product ids that receive 404 not found error
def save_404_error(data):
    os.makedirs("output_raw/error", exist_ok=True)
    check_not_exist = not os.path.exists("output_raw/error/error_404_code.csv")
    with open("output_raw/error/error_404_code.csv", "a", encoding="utf-8", newline="") as wf:
        writer = csv.writer(wf)
        if check_not_exist:
            writer.writerow(["product_id", "code"])
        for pd_id, code in data:
            writer.writerow([pd_id, code])
    print(f"Have saved {len(data)} \"404\" errors into output_raw/error/error_404_code.csv")

# save all product ids that receive timeout error => fetch again later
def save_timeout_error(data):
    os.makedirs("output_raw/error", exist_ok=True)
    check_not_exist = not os.path.exists("output_raw/error/timeout_error.csv")
    with open("output_raw/error/timeout_error.csv", "a", encoding="utf-8", newline="") as wf:
        writer = csv.writer(wf)
        if check_not_exist:
            writer.writerow(["product_id"])
        for pd_id in data:
            writer.writerow([pd_id])
    print(f"Have saved {len(data)} timeout errors into output_raw/error/timeout_error.csv")

# save checkpoint - prevent unexpected error like server die, network error,....
def save_checkpoint(checkpoint_batch):
    os.makedirs("output_raw/checkpoint", exist_ok=True)
    with open("output_raw/checkpoint/checkpoint.txt", "w", encoding="utf-8") as wf:
        wf.write(str(checkpoint_batch))

# read checkpoint to get the latest batch => continue fetch data with the latest batch
def load_checkpoint():
    if os.path.exists("output_raw/checkpoint/checkpoint.txt"):
        with open("output_raw/checkpoint/checkpoint.txt", "r", encoding="utf-8") as rf:
            return int(rf.read())
    else:
        return 1

# Main
if __name__ == "__main__":
    start_time = time.time()
    collect_data("id_product.csv")
    end_time = time.time()
    duration = end_time - start_time
    print(f"\nCompleted in {duration:.2f} seconds")