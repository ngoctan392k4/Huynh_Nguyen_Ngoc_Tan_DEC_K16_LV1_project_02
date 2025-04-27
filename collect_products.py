import requests
import time
from tqdm import tqdm
import csv
from multiprocessing import Pool, cpu_count
import json

def fetch_data(product_id):
    max_tries = 5 # if catch errors, try again until attempt = 5
    for attempt in range(max_tries):
        try:
            # Ensure that we request API like a real person => Tiki avoid DDOS
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
                if images and isinstance(images, list):
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
                if attempt == max_tries - 1:
                    return {
                        "status": "http_error",
                        "product_id": product_id,
                        "response_code": response.status_code
                    }
                else:
                    time.sleep(2)
        except requests.RequestException as e:
            print(f"\nAttempt {attempt+1} with product id {product_id}: {e}")
            if attempt == max_tries - 1:
                return {
                    "status": "timeout_error",
                    "product_id": product_id
                }
            else:
                time.sleep(2)


def collect_data(csv_file, part_size=1000):
    product_ids = []
    http_errors = []
    timeout_errors = []
    collected = []
    part = 1

    # Read all product ids
    with open(csv_file, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            pd_id = row.get("product_id")
            if pd_id:
                product_ids.append(pd_id)

    # Process with max_worker product ids at the same time => faster
    # imap_unordered allows it receive fetched without ordering => No wait => faster
    max_worker = cpu_count() * 2
    with Pool(processes=max_worker) as pool:
        for result in tqdm(pool.imap_unordered(fetch_data, product_ids), total=len(product_ids)):
            if isinstance(result, dict) and "status" in result:
                if result["status"] == "http_error":
                    http_errors.append((result["product_id"], result["response_code"]))
                elif result["status"] == "timeout_error":
                    timeout_errors.append(result["product_id"])
            else:
                collected.append(result)

            if len(collected) == part_size:
                save_products(collected, part)
                collected = []
                part+=1
        if collected:
            save_products(collected, part)

        save_http_error(http_errors)
        save_timeout_error(timeout_errors)

def save_products(data, part):
    file_name = f"output_raw/product_part{part}.json"
    with open (file_name, "w", encoding="utf-8") as wf:
        json.dump(data, wf, ensure_ascii=False, indent=2)
    print(f"Have saved {len(data)} products into {file_name}")


def save_http_error(data):
    file_name = f"output_raw/error/http_error.json"
    with open (file_name, "w", encoding="utf-8") as wf:
        json.dump(data, wf, ensure_ascii=False, indent=2)
    print(f"Have saved {len(data)} HTTP errors into {file_name}")

def save_timeout_error(data):
    file_name = f"output_raw/error/timeout_error.csv"
    with open (file_name, "w", encoding="utf-8") as wf:
        writer = csv.writer(wf)
        writer.writerow(["product_id"])
        for pd_id in data:
            writer.writerow([pd_id])
    print(f"Have saved {len(data)} TIMEOUT errors into {file_name}")

if __name__ == "__main__":
    start_time = time.time()
    collect_data("id_product.csv")
    end_time = time.time()
    duration = end_time - start_time
    print(f"\nCompleted in {duration:.2f}")